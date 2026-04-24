from app.schemas import GitHubRepo,RepoWithScore,LanguageBreakdown
from collections import Counter
from datetime import datetime,timezone,timedelta

def calculate_stars_and_forks(repos : list[GitHubRepo]) -> tuple[int,int]:
    """Calculates the total stars and forks for original works."""

    total_stars ,total_forks = 0, 0
    original_repos = [repo for repo in repos if not repo.fork] 
    
    for r in original_repos:
        total_forks +=  r.forks
        total_stars +=  r.stars

    return total_stars,total_forks


def calculate_language_breakdown(repos : list[GitHubRepo]) -> list[LanguageBreakdown]:
    """Optimized language analysis by aggregating primary language data and avoiding redundant API calls."""

    original_repos = [repo for repo in repos if not repo.fork]
    if not original_repos:
        return []

    lang_counts = Counter([r.language for r in original_repos if r.language])  # Count occurrences of each language
    n = sum(lang_counts.values())   #n is the total primary languages used 

    breakdown = []
    for lang, count in lang_counts.items():
        percentage = round((count / n) * 100, 2)  #each lang's % calculation
        breakdown.append(LanguageBreakdown(language=lang, percentage=percentage))

    return sorted(breakdown, key=lambda l: l.percentage, reverse=True) # Sort by percentage descending

#helper function for calculate_repo_quality_score
def is_recent(date_str : str) -> bool:
    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))  #The "Z" in the timestamp stands for UTC,so we parse it as such
    
    now = datetime.now(timezone.utc)   #gives the current time in utc

    difference = now - date
    return difference < timedelta(days = 30)  


def calculate_repo_quality_score(repos : list[GitHubRepo]) -> list[RepoWithScore]:
    """ Calculate repo_quality_score for each repo"""

    repos_with_scores = []

    for repo in repos:
        score = 0
    
        score += min(repo.stars * 5, 20) # 5 points per star,capped at 20
        score += min(repo.forks * 5,20)
        score += 10 if repo.description else 0
        score += 10 if is_recent(repo.updated_at) else 0
        score += min(len(repo.topics) * 2, 20) # 2 points per topic, capped at 20
        score += 10 if repo.license else 0
        score = (score + 10) if not repo.fork else (score*0.2)

        score = min(score,100) 

        repos_with_scores.append(RepoWithScore(**repo.model_dump(by_alias=False),quality_score = int(score))) 
        #Pydantic serializes using the field name (stars) instead of using the alias(stargazers_count)

    return sorted(repos_with_scores,key = lambda r : r.quality_score,reverse=True)  #Sort the repos based on their scores


def get_top_repos(repos : list[RepoWithScore],n : int = 4) -> list[RepoWithScore]:
    """Returns the top 4 original repositories based on repo_quality_score"""

    original_repos = list(filter(lambda r : not r.fork ,repos))      # r is object of RepoWithScore which has access to GithubRepo as well
    
    if len(original_repos) < n :
        return original_repos

    return original_repos[:n]