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

def get_profile_actionable_tip(score_data: ProfileScore) -> str:
    """Analyzes the score breakdown and returns the most impactful tip to improve the score."""

    if score_data.total_score >= 90:
        return "Your profile looks professional and complete! Keep maintaining your recent activity."

        
    missing_criteria = [c for c in score_data.breakdown if not c.met]   #type of c is ScoreCriterion which has fields label,met,point_possible,points_earned
        
    if not missing_criteria:
        return "You've checked all the basic boxes! Focus on gaining more community trust (stars) to boost your score further."

    missing_criteria.sort(key=lambda c: c.points_possible, reverse=True)   # Sort by possible points descending to suggest the biggest 'win' first
        
    top_missing = missing_criteria[0]   #type of top_missing is also ScoreCriterion
        
    tips_map = {
            "Identity: Bio": "Write a short bio to tell the world what you're passionate about.",
            "Identity: Social Link (X/Twitter)": "Link your X account to build more social credibility.",
            "Identity: Personal Blog/Website": "Adding a link to your portfolio or blog is a great way to showcase your deep dives.",
            "Work: Profile README": "Create a repository named after your username to build a Profile README—it's your digital resume!",
            "Work: Original Repos (>3)": "Keep building! Having at least 3 original projects shows a strong body of work.",
            "Work: Community Trust (Stars > 10)": "Improve your project READMEs and share them on social media to earn more stars.",
            "Work: Follower Milestone (>5)": "Network with other developers bysharing your work on LinkedIn or Twitter to get your first 5 followers and build social proof.",
            "Signal: Recent Activity (Last 30d)": "It looks like you've been away! Make a small commit or open an issue to show you're active.",
            "Signal: Active Maintenance (>30% repos updated)": "Dust off your old projects! Updating them shows you're a reliable maintainer."
        }

    return tips_map.get(top_missing.label, f"Focus on completing the '{top_missing.label}' milestone to boost your score.")   #If identity is email or location,then a default tip is returned


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
    total_repos = user.public_repos
    total_stars = sum(r.stars for r in repos)
    total_followers = user.followers

    has_readme = False
    for r in repos:
        if r.name == user.login:
            has_readme = True 
            break
    
    work_criteria = [
        ("Profile README", has_readme, 15),
        ("Original Repos (>3)", total_repos > 3, 10),            #We can consider forked projects as well
        ("Community Trust (Stars > 10)", total_stars > 10,8),
        ("Follower Milestone (>5)",total_followers > 5,7)
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
    sixty_days_ago = datetime.now(timezone.utc) - timedelta(days = 60)             #sixty_days_ago looks like datetime.datetime(2026, 2, 23, 16, 48, 55, 978810, tzinfo=datetime.timezone.utc)

    updated_recently = 0

    for r in repos:
        updated_at = datetime.fromisoformat(r.updated_at.replace("Z", "+00:00"))    #if updated_at = "2025-10-17T15:42:06Z",then it looks like datetime.datetime(2025, 10, 17, 15, 42, 6, tzinfo=datetime.timezone.utc)
        if updated_at <  sixty_days_ago:
            updated_recently += 1
    
    active_maintenance = (updated_recently / len(repos) >= 0.3) if repos else False

    consistency_criteria = [
        ("Recent Activity (Last 30d)", has_recent_activity, 15),
        ("Active Maintenance (>30% repos updated)", active_maintenance, 15)
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