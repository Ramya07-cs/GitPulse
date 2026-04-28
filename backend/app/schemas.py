from typing import Optional,Annotated,Literal
from pydantic import BaseModel,Field,ConfigDict

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
    blog: Optional[str] = None

#this serves GitHubRepo model
class License(BaseModel):
    key : str
    name : str

class GitHubRepo(BaseModel):

    model_config = ConfigDict(populate_by_name=True)  # this allows constructing this model using the Python field name "stars"

    name : str
    description : Optional[str] = None
    fork : Annotated[bool,Field(description="Is the repo forked?")]
    forks : Annotated[int,Field(description="Total forks for repo")]  
    topics : list[str] = []
    updated_at : str
    html_url : str
    license : Optional[License] = None
    stars : Annotated[int,Field(description="Total stars for repo",validation_alias="stargazers_count")]     
    language : Optional[str] = None  #this just gives the primary lang,but for lang breakdown u need to fetch the langs from languages_url,with 50+ repos that's 50+ calls.
    # languages_url : str    
    

#this serves GitHubEvent
class Repo(BaseModel):
    name : str

#these models are written ,bcz only these fields are required
class PullRequestPayload(BaseModel):
    merged: bool = False

class GitHubEventPayload(BaseModel):
    action: Optional[str] = None
    size: Optional[int] = None         # PushEvent
    commits: Optional[list] = None    # PushEvent
    ref_type: Optional[str] = None    # CreateEvent,DeleteEvent
    pull_request: Optional[PullRequestPayload] = None  # PullRequestEvent

class GitHubEvent(BaseModel):
    type : Annotated[str,Field(description = "GitHub event type")]
    created_at : str
    repo : Repo                    #we only need repo["name"]
    payload : GitHubEventPayload  #this is polymorphic,hence the structure varies for different events

#this serves RepoStats
class LanguageBreakdown(BaseModel):
    language : str
    percentage : float

class RepoWithScore(GitHubRepo):     # Inherits all GitHubRepo fields (including model_config) — response is flat, not nested.
    quality_score : int = 0

class RepoStats(BaseModel):
    total_stars : int
    total_forks : int
    language_breakdown: list[LanguageBreakdown]
    top_repositories : list[RepoWithScore]

class EventSummary(BaseModel):
    event_type : str
    repository : str
    time_ago : str

class CollaborationBreakdown(BaseModel):
    pr_opened: int = 0
    pr_merged: int = 0
    issues: int = 0
    comments: int = 0
    pushes : int = 0

class CollaborationScore(BaseModel):
    score: int
    badge: str
    color: str  # Hex code for the badge color
    breakdown: CollaborationBreakdown
    
class ActivityInsights(BaseModel):
    most_active_day: str
    most_active_hour: str 
    heatmap : list[list[int]]                   # grid size is 7*24 where 7 rows = Mon–Sun, 24 cols = hours 0–23, values = impact weights
    recent_events : list[EventSummary]

class ScoreCriterion(BaseModel):
    label: str           
    met: bool
    points_earned: int
    points_possible: int

class ProfileScore(BaseModel):
    total_score: int
    breakdown: list[ScoreCriterion]

class Options(BaseModel):
    tech_stack : dict[str,list[str]]
    social_links : list[str]    
    themes : list[str]

class SocialLink(BaseModel):
    platform: str
    url: str

class ReadmeRequest(BaseModel):
    # Pre-filled from dashboard — frontend sends back what it already has
    name : str
    bio_text : str
    top_repos: list[str]          # just repo names, top 3
    primary_languages : list[str]
    profile_score: int
    collaboration_badge: str
    interests : str

    # Tech stack — all checked items as one flat list
    tech_stack: list[str] = []

    # Optional personal fields
    role: Annotated[Optional[str],Field(max_length=100)] = None
    open_to_work: bool = False
    fun_fact: Optional[str] = None
    quote: Optional[str] = None

    # Social — pre-filled from GitHub data + user additions
    twitter: Optional[str] = None
    blog: Optional[str] = None
    social_links: list[SocialLink] = []

    #theme for stats card and streak card
    theme : str = "dark"

    # Toggle states — which sections to include
    include_stats_card: bool = True
    include_streak_card: bool = True
    include_repo_cards: bool = True
    include_language_badges: bool = True
    include_social_links: bool = True
    include_score_badges: bool = True 
    include_most_used_languages: bool = True  
    include_profile_views: bool = True

class ReadmeResponse(BaseModel):
    markdown: str       #the full generated README string
    username: str
    
class DashBoardResponse(BaseModel):
    profile : GitHubUser
    repositories : list[RepoWithScore]
    repo_stats: RepoStats
    activity_insights: ActivityInsights
    collaboration_score : CollaborationScore
    profile_score : ProfileScore
    actionable_tip : str