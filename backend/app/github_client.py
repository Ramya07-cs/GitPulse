import os
import httpx
from dotenv import load_dotenv
from app.schemas import GitHubUser
from fastapi import HTTPException

load_dotenv()  #Load environment variables from .env file

#required for making authorized requests so that u can make 5,000 requests/hour else it would just be 60 requests/hour
headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}   

async def fetch_user(username : str) -> GitHubUser:
    async with httpx.AsyncClient() as client:   
        response = await client.get("https://api.github.com/users/{}".format(username), headers = headers)  

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")

        if response.status_code == 403:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        data = response.json()   # response can't be passed to model directly
        return GitHubUser(**data)    

