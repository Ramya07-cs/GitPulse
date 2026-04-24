from app.schemas import GitHubUser,GitHubEvent,GitHubRepo,CollaborationBreakdown,CollaborationScore,ScoreCriterion,ProfileScore
from datetime import datetime,timezone,timedelta

#This is based on 1-month activity bcz of api restriction
def calculate_collaboration_score(events: list[GitHubEvent], username: str, repos: list[GitHubRepo]) -> CollaborationScore:

    breakdown = CollaborationBreakdown()

    social_points = 0
    push_points = 0      #In order to avoid dominance of push events alone
    
    forked_repos = {repo.name for repo in repos if repo.fork}

    for event in events:
        event_type = event.type
        payload = event.payload
        
        full_repo_path = event.repo.name # e.g.,"Ramya07-cs/GitPulse"
        repo_name = full_repo_path.split("/")[-1] # "GitPulse"

        is_own_repo = full_repo_path.startswith(f"{username}/")  #Check ownership using the full path before splitting
        is_fork = repo_name in forked_repos
        

        # Multipliers which distinguishes if the work was done as solo/team to consider social activeness
        if not is_own_repo:
            multiplier = 2.0       #External - Not owned by user
        elif is_fork:
            multiplier = 1.0       #Forked - Owned by user but a fork
        else:
            multiplier = 0.5       #Solo - Owned by user and is original work

        if event_type == "PushEvent":
            push_points += (5 * multiplier)
            breakdown.pushes += 1

        if event_type == "PullRequestEvent":
            if payload.action == "opened":
                social_points += (15 * multiplier)
                breakdown.pr_opened += 1
            
            if payload.pull_request and payload.pull_request.merged:    # Merged check
                social_points += (20 * multiplier)
                breakdown.pr_merged += 1
                
        elif event_type == "IssuesEvent":
            if payload.action in ["opened", "closed"]:
                social_points += (5 * multiplier)
                breakdown.issues += 1
                
        elif event_type == "IssueCommentEvent":
            social_points += (2 * multiplier)
            breakdown.comments += 1

    final_push_score = min(30, int(push_points))          #Cap Push Points at 30% of the maximum possible score
    final_score = min(100, int(final_push_score + social_points))    # Cap at 100
    
    # Badge Mapping
    if final_score >= 80:
        badge, color = "Top Contributor", "#7C3AED"      #consistent PR activity with good merge rate
    elif final_score > 60:
        badge, color = "Active Collaborator", "#2563EB"   #has accepted PRs or regular issue engagement
    elif final_score > 30:
        badge, color = "Building Momentum", "#059669"     #has some issues/PRs but no accepted PRs yet
    else:      
        badge, color = "Solo Developer", "#6B7280"        #only PushEvents, no PRs or issues

    return CollaborationScore(
        score=final_score,
        badge=badge,
        color=color,
        breakdown=breakdown         #useful for frontend
    )

def calculate_profile_score(user: GitHubUser, repos: list[GitHubRepo], events: list[GitHubEvent]) -> ProfileScore:
    breakdown = []
    
    # Identity Completeness (Max 30)
    identity_fields = [
        ("Bio", user.bio, 10),
        ("Location", user.location, 5),
        ("Email", user.email, 5),
        ("Social Link (X/Twitter)", user.twitter_username, 5),
        ("Personal Blog/Website", user.blog, 5)
    ]
    
    for label, field, points in identity_fields:

        is_met = bool(field)
        breakdown.append(ScoreCriterion(label=f"Identity: {label}",
                                        met=is_met,
                                        points_earned=points if is_met else 0,
                                        points_possible=points))

    # Work Evidence (Max 40)
    original_repos = [r for r in repos if not r.fork]
    total_stars = sum(r.stars for r in original_repos)

    has_readme = False
    for r in original_repos:
        if r.name == user.login:
            has_readme = True 
            break
    
    work_criteria = [
        ("Profile README", has_readme, 15),
        ("Original Repos (>3)", len(original_repos) >= 3, 10),
        ("Community Trust (Stars > 10)", total_stars >= 10, 15)
    ]
    
    for label, met, points in work_criteria:
        breakdown.append(ScoreCriterion(
            label=f"Work: {label}",
            met=met,
            points_earned=points if met else 0,
            points_possible=points
        ))

    #  Consistency Signal (Max 30) 
    has_recent_activity = len(events) > 0  # Check for any activity in last 30 days
    
    # Check % of repos updated in last 60 days
    sixty_days_ago = datetime.now(timezone.utc) - timedelta(days = 60)  

    updated_recently = 0

    for r in original_repos:
        updated_at = datetime.fromisoformat(r.updated_at.replace("Z", "+00:00"))
        if updated_at <  sixty_days_ago:
            updated_recently += 1
    
    active_maintenance = (updated_recently / len(original_repos) >= 0.3) if original_repos else False

    consistency_criteria = [
        ("Recent Activity (Last 30d)", has_recent_activity, 15),
        ("Active Maintenance (>30% repos)", active_maintenance, 15)
    ]

    for label, met, points in consistency_criteria:
        breakdown.append(ScoreCriterion(
            label=f"Signal: {label}",
            met=met,
            points_earned=points if met else 0,
            points_possible=points
        ))

    total_earned = sum(c.points_earned for c in breakdown)

    return ProfileScore(total_score=total_earned, breakdown=breakdown)