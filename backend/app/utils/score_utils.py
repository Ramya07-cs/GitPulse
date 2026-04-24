from app.schemas import GitHubEvent,GitHubRepo,CollaborationBreakdown,CollaborationScore


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