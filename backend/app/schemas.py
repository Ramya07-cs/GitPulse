from typing import Optional,Annotated
from pydantic import BaseModel

class GitHubUser(BaseModel):
    #Only these fields are required from raw user data
    login : str
    name : Optional[str] = None
    bio: Optional[str] = None
    id : int
    location : Optional[str]
    public_repos: int
    followers : int
    avatar_url: str
    created_at : str
    updated_at : str
    email : Optional[str] = None
    twitter_username: Optional[str] = None