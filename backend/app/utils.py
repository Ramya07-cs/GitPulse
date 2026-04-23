from typing import Tuple
from app.schemas import *
from collections import Counter
from datetime import datetime,timedelta,timezone


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


def calculate_stars_and_forks(repos : list[GitHubRepo]) -> Tuple[int,int]:
    """Calculates the total stars and forks for original works."""
    total_stars ,total_forks = 0, 0
    original_repos = [repo for repo in repos if not repo.fork] 
    
    for r in original_repos:
        total_forks +=  r.forks
        total_stars +=  r.stars

    return total_stars,total_forks


def calculate_language_breakdown(repos : list[GitHubRepo]) -> list[LanguageBreakdown]:
    """Optimized language analysis by aggregating primary language data and avoiding redundant API calls."""

    original_repos = [repo for repo in repos if not repo.fork]
    if not original_repos:
        return []

    lang_counts = Counter([r.language for r in original_repos if r.language])  # Count occurrences of each language
    total_langs = n = sum(lang_counts.values())

    breakdown = []
    for lang, count in lang_counts.items():
        percentage = round((count / n) * 100, 2)  #each lang's % calculation
        breakdown.append(LanguageBreakdown(language=lang, percentage=percentage))

    return sorted(breakdown, key=lambda l: l.percentage, reverse=True) # Sort by percentage descending


def is_recent(date_str : str) -> bool:
    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))  #The "Z" in the timestamp stands for UTC,so we parse it as such
    
    now = datetime.now(timezone.utc)   #gives the current time in utc

    difference = now - date
    return difference < timedelta(days = 30)  


def calculate_repo_quality_score(repos : list[GitHubRepo]) -> list[RepoWithScore]:
    """ Calculate repo_quality_score for each repo"""
    repos_with_scores = []

    for repo in repos:
        score = 0
    
        score += min(repo.stars * 5, 20) # 5 points per star,capped at 20
        score += min(repo.forks * 5,20)
        score += 10 if repo.description else 0
        score += 10 if is_recent(repo.updated_at) else 0
        score += min(len(repo.topics) * 2, 20) # 2 points per topic, capped at 20
        score += 10 if repo.license else 0
        score = score + 10 if not repo.fork else score*0.2

        score = min(score,100) 

        repos_with_scores.append(RepoWithScore(repo = repo,quality_score = int(score))) 

    return sorted(repos_with_scores,key = lambda r : r.quality_score,reverse=True)  #Sort the repos based on their scores


def get_top_repos(repos : list[RepoWithScore],n : int = 4) -> list[RepoWithScore]:
    """Returns the top 4 original repositories based on repo_quality_score"""

    original_repos = list(filter(lambda r : not r.repo.fork ,repos))
    
    if len(original_repos) < n :
        return original_repos

    return original_repos[:n]


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

    
def recent_events(events : list[GitHubEvent],n : int = 5) -> list[EventSummary]:

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
        return ActivityInsights(most_active_day = "N/A",most_active_hour="N/A",heatmap = [0],recent_events = [])

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
    readable_hour = datetime.strptime(str(peak_hour), "%H").strftime("%I %p")   #Time is in utc

    sorted_events = sorted(events,key = lambda e : e.created_at,reverse=True)
    most_recent_events = recent_events(sorted_events)

    return ActivityInsights(most_active_day = most_active_day,most_active_hour=readable_hour,heatmap = heatmap_grid,recent_events = most_recent_events)