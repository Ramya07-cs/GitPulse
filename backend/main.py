#This file receives the request, calls a function from another file, and returns the final JSON response to the user.
from fastapi import FastAPI,Path,Query
from typing import Annotated
from app.github_client import fetch_user,fetch_repos
from app.schemas import GitHubUser,GitHubRepo
from typing import Literal

app = FastAPI(title="GitPulse")

@app.get("/")
def health():
    return {"status" : "ok","message":"GitPulse is running"}  

@app.get("/user/{username}")
async def get_user( username : Annotated[str,Path(description="Enter a github username")] ) -> GitHubUser:
    return await fetch_user(username)

@app.get("/user/{username}/repos")
async def get_repos(username : str,repo_type : str = "owner",per_page : int = Query(default=100,gt=0,le=100),sort : Literal["created","updated","full_name","pushed"] = "updated") -> list[GitHubRepo]:
    return await fetch_repos(username,repo_type,per_page,sort)