from typing import Optional,Annotated,Literal
from pydantic import BaseModel,Field

class GitHubUser(BaseModel):
    #Only these fields are required from raw user data
    login : str
    name : Optional[str] = None
    bio: Optional[str] = None
    id : int
    location : Optional[str] = None
    public_repos: int
    followers : int    
    html_url : str
    avatar_url: str
    created_at : str
    updated_at : str
    email : Optional[str] = None
    twitter_username: Optional[str] = None

#this serves GitHubRepo model
class License(BaseModel):
    key : str
    name : str

class GitHubRepo(BaseModel):
    name : str
    description : Optional[str] = None
    fork : Annotated[bool,Field(description="Is the repo forked?")]
    forks : Annotated[int,Field(description="Total forks for repo")]  
    topics : list[str] = []
    updated_at : str
    html_url : str
    license : Optional[License] = None
    stars : Annotated[int,Field(description="Total stars for repo",validation_alias="stargazers_count")] 
    language : Optional[str] = None  #this just gives the primary lang,but for lang breakdown u need to fetch the langs from languages_url,
                                     #that would again make 51 api calls if the user has 50 repos,which is a huge mess!!!!!
    '''
    #later,we can implement db as mentioned in issue #15 
    languages_url : str
    '''
#this serves GitHubEvent
class Repo(BaseModel):
    name : str

#these models are written ,bcz only these fields are required
class PullRequestPayload(BaseModel):
    merged: bool = False

class GitHubEventPayload(BaseModel):
    action: Optional[str] = None
    size: Optional[int] = None
    commits: Optional[list] = None    # * PushEvent
    ref_type: Optional[str] = None    # * CreateEvent,DeleteEvent
    pull_request: Optional[PullRequestPayload] = None  # * PullRequestEvent

class GitHubEvent(BaseModel):
    type : Annotated[str,Field(description = "Event type")]
    created_at : str
    repo : Repo  #we only need repo["name"]
    payload : GitHubEventPayload  #this is polymorphic,hence the structure varies for different events

#this serves RepoStats
class LanguageBreakdown(BaseModel):
    language : str
    percentage : float

class RepoWithScore(BaseModel):
    repo : GitHubRepo
    quality_score : int = 0

class RepoStats(BaseModel):
    total_stars : int
    total_forks : int
    language_breakdown: list[LanguageBreakdown]
    top_repositories : list[RepoWithScore]

class EventSummary(BaseModel):
    event : GitHubEvent
    time_ago : str
    
class ActivityInsights(BaseModel):
    most_active_day: str
    most_active_hour: str
    heatmap : list[list[int]]
    #recent_events : list[EventSummary]

class DashBoardResponse(BaseModel):
    profile : GitHubUser
    repositories : list[RepoWithScore]
    repo_stats: RepoStats
    activity_insights: ActivityInsights