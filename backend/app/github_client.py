import os
import httpx
from dotenv import load_dotenv
from app.schemas import GitHubUser,GitHubRepo,GitHubEvent
from fastapi import HTTPException
from typing import Literal,Optional
from datetime import datetime,timezone
import asyncio

load_dotenv()  #Load environment variables from .env file

#Required for making authenticated requests: 5,000 req/hour. Without token: 60 req/hour.
headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}   


def calculate_reset_time(response : httpx.Response) -> Optional[str]:
    """Reads the x-ratelimit-reset header and returns a human-readable UTC reset time."""

    timestamp = response.headers.get("x-ratelimit-reset")  #returns a Unix timestamp as a string
    if not timestamp:  #if 403 wasn't bcz of rate limit
        return None
    reset_time = datetime.fromtimestamp(int(timestamp),tz=timezone.utc).strftime("%I:%M %p")          #Time shown is in UTC
    
    return reset_time


async def fetch_user(username : str) -> GitHubUser:
    """Fetches public profile data for a GitHub user."""

    async with httpx.AsyncClient() as client:   
        response = await client.get("https://api.github.com/users/{}".format(username), headers = headers)  

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")

        if response.status_code == 403:
            raise HTTPException(status_code=429, detail=f"Limit resets at {calculate_reset_time(response)}")

        data = response.json()   # response can't be passed to model directly
        return GitHubUser(**data)    


async def fetch_repos(username : str,
                    repo_type : str = "owner",
                    per_page : int = 100,
                    sort : Literal["created","updated","full_name","pushed"] = "updated") -> list[GitHubRepo]:
    """Fetches all public repositories for a user."""

    async with httpx.AsyncClient() as client:    
        response = await client.get("https://api.github.com/users/{}/repos?type={}&per_page={}&sort={}".format(username,repo_type,per_page,sort),headers = headers)

        if response.status_code == 404:
            raise HTTPException(status_code=404,detail = "User not found")

        if response.status_code == 403:
            raise HTTPException(status_code=429, detail=f"Limit resets at {calculate_reset_time(response)}")

        repos = response.json()
        if not repos:   #If the user exists but has no public repos,just return an empty list
            return []

        return [GitHubRepo(**repo) for repo in repos]


async def fetch_events(username : str, per_page : int = 100,page : int = 1) -> list[GitHubEvent]:
    """Fetches all types of events.GitHub RestAPI returns max 300 events across 3 pages (100 per page).Only covers approximately the last 30 days of activity."""

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/users/{}/events?per_page={}&page={}".format(username,per_page,page),headers = headers)

        if response.status_code == 404:
            raise HTTPException(status_code=404,detail = "User not found")

        if response.status_code == 403:
            raise HTTPException(status_code=429, detail=f"Limit resets at {calculate_reset_time(response)}")

        events = response.json()

        if not events: 
            return []

        return [GitHubEvent(**event) for event in events]   


async def fetch_all_events(username: str) -> list[GitHubEvent]:
    """Fetches up to 300 events across 3 pages."""

    page1 = await fetch_events(username, page=1)
    if len(page1) < 100:  
        return page1

    #the user is active and hence there is possibility of having events in page 2 and 3
    page2, page3 = await asyncio.gather(fetch_events(username, page=2),fetch_events(username, page=3))

    return page1 + page2 + page3 