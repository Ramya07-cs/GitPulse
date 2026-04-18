#This file receives the request, calls a function from another file, and returns the final JSON response to the user.
from fastapi import FastAPI,Path
from typing import Annotated
from app.github_client import fetch_user
from app.schemas import GitHubUser

app = FastAPI(title="GitPulse")

@app.get("/")
def health():
    return {"status" : "ok","message":"GitPulse is running"}  

@app.get("/user/{username}")
async def get_user(username : Annotated[str,Path(description="Enter a github username")]) -> GitHubUser:
    return await fetch_user(username)

