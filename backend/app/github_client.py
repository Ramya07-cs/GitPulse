import os
import httpx
from dotenv import load_dotenv
from app.schemas import GitHubUser,GitHubRepo
from fastapi import HTTPException,Query
from typing import Literal,Optional

load_dotenv()  #Load environment variables from .env file

#required for making authorized requests so that u can make 5,000 requests/hour else it would just be 60 requests/hour
headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}   

#fetches the basic user info
async def fetch_user(username : str) -> GitHubUser:
    async with httpx.AsyncClient() as client:   
        response = await client.get("https://api.github.com/users/{}".format(username), headers = headers)  

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")

        if response.status_code == 403:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        data = response.json()   # response can't be passed to model directly
        return GitHubUser(**data)    

#fetches all the public repos of the user and returns only the fields in GitHubRepo model for every repo as a list
async def fetch_repos(username : str,repo_type : str = "owner",per_page : int = Query(default=100,gt=0,le=100),sort : Literal["created","updated","full_name","pushed"] = "updated") -> list[GitHubRepo]:
    async with httpx.AsyncClient() as client:    
        response = await client.get("https://api.github.com/users/{}/repos?type={}&per_page={}&sort={}".format(username,repo_type,per_page,sort),headers = headers)

        if response.status_code == 404:
            raise HTTPException(status_code=404,detail = "User not found")

        repos = response.json()
        if response.status_code == 200 and not repos:   #If the user exists but has no public repos,just return an empty list
            return []
        return [GitHubRepo(**repo) for repo in repos]