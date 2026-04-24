from fastapi import FastAPI,Path,Query
from typing import Annotated,Literal
from app.github_client import fetch_user,fetch_repos,fetch_all_events
from app.schemas import GitHubUser, GitHubRepo, GitHubEvent, RepoStats, DashBoardResponse
from app.utils.repo_utils import calculate_stars_and_forks, calculate_language_breakdown, calculate_repo_quality_score, get_top_repos
from app.utils.event_utils import analyse_activity
from app.utils.score_utils import calculate_collaboration_score,calculate_profile_score
import asyncio

app = FastAPI(title="GitPulse")

@app.get("/")
def health():
    return {"status" : "ok","message":"GitPulse is running"}  

#These routes are working perfect individually when tested,now we can combine them using asyncio.gather()

@app.get("/user/{username}",response_model = GitHubUser )
async def get_user( username : Annotated[str,Path(description="Enter a github username")] ):
    return await fetch_user(username)

@app.get("/user/{username}/repos",response_model = list[GitHubRepo])
async def get_repos(username : str,
                    repo_type : str = "owner",
                    per_page : int = Query(default=100,gt=0,le=100),
                    sort : Literal["created","updated","full_name","pushed"] = "updated"):
    return await fetch_repos(username,repo_type,per_page,sort)

@app.get("/user/{username}/events",response_model=list[GitHubEvent])
async def get_events(username : str,per_page : int = Query(default=100,gt=0,le=100),page : int = Query(default=1,gt = 0,le = 3)):
    page1 =  await fetch_events(username)
    
    if len(page1) == 100:    
            page2, page3 = await asyncio.gather(fetch_events(username,page = 2),fetch_events(username,page = 3))
            return page1 + page2 + page3
    return page1


#we'll fetch all data at once and analyse it
@app.get("/analyse/{username}/dashboard",response_model = DashBoardResponse)
async def analyse_profile(username : str):
    user, repos, events =  await asyncio.gather(fetch_user(username),fetch_repos(username),fetch_all_events(username))

    stars, forks = calculate_stars_and_forks(repos)

    lang_analysis = calculate_language_breakdown(repos)

    repos_with_scores = calculate_repo_quality_score(repos)

    top_repos = get_top_repos(repos_with_scores)

    activity_stats = analyse_activity(events)

    collab_score = calculate_collaboration_score(events, username, repos)
    
    profile_score_data = calculate_profile_score(user, repos, events)

    return DashBoardResponse(profile = user,
                            repositories = repos_with_scores,
                            repo_stats = RepoStats(total_stars = stars,total_forks = forks,language_breakdown = lang_analysis,top_repositories = top_repos),
                            activity_insights = activity_stats,
                            collaboration_score = collab_score,
                            profile_score = profile_score_data)