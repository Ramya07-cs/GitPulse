import os
import httpx
from dotenv import load_dotenv
from app.schemas import GitHubUser,GitHubRepo,GitHubEvent
from fastapi import HTTPException
from typing import Literal,Optional
from datetime import datetime

load_dotenv()  #Load environment variables from .env file

#required for making authorized requests so that u can make 5,000 requests/hour else it would just be 60 requests/hour
headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}   

#Calculates the reset time for making authorized requests after rate limit exceeds
def calculate_reset_time(response : httpx.Response) -> Optional[str]:

    timestamp = response.headers.get("x-ratelimit-reset")  #returns a Unix timestamp as a string
    if not timestamp:  #if 403 wasn't bcz of rate limit
        return None
    reset_time = datetime.fromtimestamp(int(timestamp)).strftime("%I:%M %p")
    
    return reset_time

#fetches the basic user info
async def fetch_user(username : str) -> GitHubUser:
    async with httpx.AsyncClient() as client:   
        response = await client.get("https://api.github.com/users/{}".format(username), headers = headers)  

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")

        if response.status_code == 403:
            raise HTTPException(status_code=429, detail=f"Limit resets at {calculate_reset_time(response)}")

        data = response.json()   # response can't be passed to model directly
        return GitHubUser(**data)    

#fetches all the public repos of the user and returns only the fields in GitHubRepo model for every repo as a list
async def fetch_repos(username : str,
                    repo_type : str = "owner",
                    per_page : int = 100,
                    sort : Literal["created","updated","full_name","pushed"] = "updated") -> list[GitHubRepo]:

    async with httpx.AsyncClient() as client:    
        response = await client.get("https://api.github.com/users/{}/repos?type={}&per_page={}&sort={}".format(username,repo_type,per_page,sort),headers = headers)

        if response.status_code == 404:
            raise HTTPException(status_code=404,detail = "User not found")

        if response.status_code == 403:
            raise HTTPException(status_code=429, detail=f"Limit resets at {calculate_reset_time(response)}")

        repos = response.json()
        if response.status_code == 200 and not repos:   #If the user exists but has no public repos,just return an empty list
            return []

        return [GitHubRepo(**repo) for repo in repos]

#fetch all types of events,we'll filter based on requirement
#This gives almost 1 month user activity and a max ~300 events
async def fetch_events(username : str, per_page : int = 100,page : int = 1) -> list[GitHubEvent]:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/users/{}/events?per_page={}&page={}".format(username,per_page,page),headers = headers)

        if response.status_code == 404:
            raise HTTPException(status_code=404,detail = "User not found")

        if response.status_code == 403:
            raise HTTPException(status_code=429, detail=f"Limit resets at {calculate_reset_time(response)}")

        events = response.json()

        if response.status_code == 200 and not events: 
            return []

        return [GitHubEvent(**event) for event in events]    

"""
Types of events returned by GitHub RestAPI:
PushEvent — if user ran git push (not the same as individual commits inside a push)
PullRequestEvent — PR opened/closed/merged
IssuesEvent — issue opened/closed
IssueCommentEvent — comment posted on an issue
CreateEvent — branch or repo created
DeleteEvent — branch deleted
WatchEvent — if user starred a repo
PublicEvent — repo made public
ForkEvent — repo forked
"""