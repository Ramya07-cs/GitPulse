from fastapi import FastAPI,Path,Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from typing import Annotated,Literal

from app.github_client import fetch_user,fetch_repos,fetch_all_events
from app.schemas import RepoStats, DashBoardResponse,ReadmeRequest,ReadmeResponse,Options

from app.utils.repo_utils import calculate_stars_and_forks, calculate_language_breakdown, calculate_repo_quality_score, get_top_repos
from app.utils.event_utils import analyse_activity
from app.utils.score_utils import calculate_collaboration_score,calculate_profile_score,get_profile_actionable_tip
from app.utils.readme_utils import generate_readme

from app.lib.social_links import SOCIAL_BADGE_MAP
from app.lib.tech_stack import STACK_BADGE_MAP

import asyncio

app = FastAPI(title="GitPulse",docs_url="/docs", redoc_url="/redoc")

#required to connect fastapi and vite
app.add_middleware(
                    CORSMiddleware,
                    allow_origins=[
                        "http://localhost:5173",
                        "http://localhost:3000",
                        "https://*.vercel.app",
                    ],
                    allow_methods=["*"],
                    allow_headers=["*"],
                    )

                    
@app.get("/",include_in_schema=False)
def root():
    return RedirectResponse(url = "/docs")    #Redirects the root URL to the interactive API documentation


@app.get("/health")
def health():
    return {"status" : "ok","message":"GitPulse is running"}  


# frontend calls this endpoint once when it loads the README config page
# then uses the data to render the category sections with toggle buttons and the theme dropdown
@app.get("/user/readme/options",response_model=Options)             
def get_options():
    return Options(tech_stack = {category : list(item.keys()) for category,item in STACK_BADGE_MAP.items()},
                    social_links =  [platform for platform in SOCIAL_BADGE_MAP.keys()],
                    themes = ["default", "dark", "github_dark", "midnight-purple", "rose", "blue_navy"]
                    )


#we'll fetch all data at once and analyse it
@app.get("/user/{username}/dashboard",response_model = DashBoardResponse)
async def analyse_profile(username : str):
    user, repos, events =  await asyncio.gather(fetch_user(username),fetch_repos(username),fetch_all_events(username))

    stars, forks = calculate_stars_and_forks(repos)

    lang_analysis = calculate_language_breakdown(repos)

    repos_with_scores = calculate_repo_quality_score(repos)

    top_repos = get_top_repos(repos_with_scores)

    activity_stats = analyse_activity(events)

    collab_score = calculate_collaboration_score(events, username, repos)
    
    profile_score_data = calculate_profile_score(user, repos, events)

    actionable_tip = get_profile_actionable_tip(profile_score_data)

    return DashBoardResponse(profile = user,
                            repositories = repos_with_scores,
                            repo_stats = RepoStats(total_stars = stars,total_forks = forks,language_breakdown = lang_analysis,top_repositories = top_repos),
                            activity_insights = activity_stats,
                            collaboration_score = collab_score,
                            profile_score = profile_score_data,
                            actionable_tip = actionable_tip)


#generates the md string based on the form inputs and toggle states           
@app.post("/user/{username}/readme",response_model= ReadmeResponse)
def create_readme(username : str,request : ReadmeRequest):
    profile_readme = generate_readme(username,request)
    return ReadmeResponse(markdown = profile_readme,username = username)
