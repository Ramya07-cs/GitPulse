"""
GitHub REST API — Event Types Reference
PushEvent         — git push (one event per push, not per commit)
PullRequestEvent  — PR opened / closed / merged
IssuesEvent       — issue opened / closed / reopened
IssueCommentEvent — comment on an issue or PR
CreateEvent       — branch, tag, or repository created
DeleteEvent       — branch or tag deleted
WatchEvent        — user starred a repo
PublicEvent       — repo made public
ForkEvent         — repo forked
"""

from app.schemas import GitHubEvent,ActivityInsights,EventSummary
from collections import Counter
from datetime import datetime,timezone

# fallback values for unhandled action variants of events in get_event_impact function
IMPACT_MAP = {
        "PushEvent" :  2, 
        "PullRequestEvent" : 2,   
        "IssuesEvent" : 1,
        "IssueCommentEvent" : 2,
        "CreateEvent" : 1,
        "DeleteEvent" : 1,          #they are all passive events
        "ForkEvent" : 1,
        "WatchEvent" : 0,      #if the user stars a repo/subscribes to notifications on
        }


#this is needed for generating heatmap and activity stats
def get_event_impact(event : GitHubEvent) -> int:
    """Returns a weight from the payload to represent the volume of work"""

    payload = event.payload
    event_type = event.type 
    
    if event_type == "PushEvent":  #the data has many inconsistencies,size and commit fields may or may not be there

        if payload.size:  #number of commits
            return min(10,payload.size )  

        elif payload.commits:    
            return min(10,len(payload.commits))   #gives the commit count for that push; 50-commit push doesn't dominate the heatmap

        else:
            return 1

    if event_type == "PullRequestEvent":   #Opening/merging PR shows more effort

        if payload.pull_request:
            #action can be "opened","closed", "reopened" or "synchronize"(a commit pushed to open PR)
            
            if payload.action == "closed":
                if payload.pull_request.merged:   #work was accepted 
                    return 8                    
                else:
                    return 3                        #work was abandoned

            elif payload.action == "opened":
                return 4           #new contribution started

            else:
                return 2       

    if event_type == "IssuesEvent":

        action = payload.action
        if action == "opened" or action == "closed":
            return 4

        elif action == "reopened":
            return 2

    if event_type == "CreateEvent":
        #ref_type can be repository,branch or tag

        if payload.ref_type == "repository":   #starting something new
            return 4
        
        elif payload.ref_type == "tag":    #signals a release
            return 3

        elif payload.ref_type == "branch":
            return 1   

    return IMPACT_MAP.get(event_type, 1)    #fallback for PublicEvent, MemberEvent, ReleaseEvent


def time_ago(date_str : str) -> str:
    
    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))  
    
    now = datetime.now(timezone.utc)   #gives the current time in utc

    difference = now - date   #gives a timedelta object 

    days = difference.days
    if days >= 1:
        if days >= 30: return "1 month ago"
        if days >= 7: return f"{days // 7}w ago"

        return f"{days}d ago"
    
    # Only check seconds if days < 1
    seconds = difference.seconds
    if seconds >= 3600:
        return f"{seconds // 3600}h ago"

    if seconds >= 60:
        return f"{seconds // 60}m ago"

    return "just now"

    
def get_recent_events(events : list[GitHubEvent],n : int = 5) -> list[EventSummary]:

    events = events[:n]        #Gives the recent n events

    events_timeline = []

    for event in events:
        time = time_ago(event.created_at)

        repo_name = event.repo.name   #repo_name looks something like "Ramya07-cs/GitPulse"
        repo_name = repo_name.split("/")[-1]

        events_timeline.append(EventSummary(event_type = event.type,repository = repo_name,time_ago = time))

    return events_timeline


def analyse_activity(events : list[GitHubEvent]) -> ActivityInsights:
    """Analyzes event patterns to determine behavior and impact."""

    #Heatmap's cells are powered by impact-weights which determine the effort,instead of frequency
    heatmap_grid = [[0 for _ in range(24)] for _ in range(7)]   

    if not events:
        return ActivityInsights(most_active_day = "N/A",most_active_hour="N/A",heatmap = heatmap_grid,recent_events = [])

    daily_impact = Counter()      #stores data in the form of list of tuples
    hourly_impact = Counter() 

    for event in events:
        impact = get_event_impact(event)

        utc_date = datetime.fromisoformat(event.created_at.replace("Z","+00:00"))  # Parse as UTC
        
        day = utc_date.strftime("%A")     #we get the day when %A is passed
        hour = utc_date.hour  #hour is an integer b/w 0 to 23

        daily_impact[day] += impact
        hourly_impact[hour] += impact

        day_index = utc_date.weekday()  #gives 0(Monday) through 6(Sunday)

        heatmap_grid[day_index][hour] += impact

    most_active_day = daily_impact.most_common(1)[0][0] if daily_impact else "N/A"

    peak_hour = hourly_impact.most_common(1)[0][0] if hourly_impact else "N/A"
    readable_hour = datetime.strptime(str(peak_hour), "%H").strftime("%I %p") if peak_hour != "N/A" else "N/A"    #Time is in utc

    sorted_events = sorted(events,key = lambda e : e.created_at,reverse=True)
    latest_events = get_recent_events(sorted_events)

    return ActivityInsights(most_active_day = most_active_day,
        most_active_hour=readable_hour,
        heatmap = heatmap_grid,
        recent_events = latest_events)