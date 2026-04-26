from app.schemas import ReadmeRequest,SocialLink
from app.lib.social_links import SOCIAL_BADGE_MAP
from app.lib.tech_stack import STACK_BADGE_MAP
from urllib.parse import quote_plus
from typing import Optional


#Helper function
def get_badge_details(name: str) -> tuple[str,str,str]:
    """Searches nested STACK_BADGE_MAP for a tech name."""

    for category in STACK_BADGE_MAP.values():
        if name in category:
            return category[name]
    return None


def build_header(username: str, role: Optional[str], open_to_work: bool) -> str:
    base_url = "https://readme-typing-svg.demolab.com"

    lines = [f"Hello%2C+I%27m+{username}"] 
    if role:
        lines.append(quote_plus(role))      #special characters cannot be used directly in urls,hence apostophe becomes %27 , comma becomes %2C and so on

    if open_to_work:
        lines.append(quote_plus("Available for Opportunities"))
    
    lines_param = ";".join(lines)

    return (
        f'<p align="center">\n'
        f'  <img src="{base_url}?font=Fira+Code&size=22&duration=3000&pause=1000&color=58A6FF&center=true&vCenter=true&width=600&lines={lines_param}" />\n'
        f'</p>'
    )

def build_language_badges(selected_stack: list[str], include: bool) -> str:
    if not include or not selected_stack:
        return ""
    
    badges = []
    for name in selected_stack:
        details = get_badge_details(name)
        if details:
            bg, logo, logo_color = details
            url = f"https://img.shields.io/badge/{quote_plus(name)}-{bg}?style=flat&logo={logo}&logoColor={logo_color}"
        else:
            # Generic gray fallback for unknown tech
            url = f"https://img.shields.io/badge/{quote_plus(name)}-gray?style=flat"

        badges.append(f"![{name}]({url})")
    
    return "###  Tech Stack\n" + " ".join(badges)

def build_stats_and_streak(username: str, theme: str, include_stats: bool, include_streak: bool) -> str:
    if not (include_stats or include_streak):
        return ""
    
    stats_url = f"https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&theme={theme}&hide_border=true"
    streak_url = f"https://streak-stats.demolab.com/?user={username}&theme={theme}&hide_border=true"
    
    content = ""
    if include_stats:
        content += f'<img src="{stats_url}" alt="Stats Card" />\n'
    if include_streak:
        content += f'<img src="{streak_url}" alt="Streak Card" />'
        
    return f'<p align="center">\n{content}\n</p>'

def build_repo_cards(username: str, top_repos: list[str], theme: str, include: bool) -> str:
    if not include or not top_repos:
        return ""
    
    base_url = "https://github-readme-stats.vercel.app/api/pin/"
    cards = [f'[![Repo]({base_url}?username={username}&repo={repo}&theme={theme})](https://github.com/{username}/{repo})' for repo in top_repos]
    
    # Arrange 2 per line
    lines = []
    for i in range(0, len(cards), 2):
        lines.append(" ".join(cards[i:i+2]))
    
    return "###  Featured Projects\n" + ("\n\n".join(lines))

def build_social_links(twitter : Optional[str], blog : Optional[str], social_links  : list[SocialLink], include) -> str:
    if not include:
        return ""
    
    badges = []
    
    connect_text = "### Let's connect on:\n"

    # Pre-filled Twitter
    if twitter:
        bg, logo, logo_color = SOCIAL_BADGE_MAP.get("Twitter", ("1DA1F2", "twitter", "white"))
        url = f"https://img.shields.io/badge/Twitter-{bg}?style=flat&logo={logo}&logoColor={logo_color}"
        badges.append(f"[![Twitter]({url})](https://twitter.com/{twitter})")
    
    # Pre-filled Blog/Portfolio
    if blog:
        bg, logo, logo_color = SOCIAL_BADGE_MAP.get("Portfolio", ("000000", "linktree", "white"))
        url = f"https://img.shields.io/badge/Portfolio-{bg}?style=flat&logo={logo}&logoColor={logo_color}"
        badges.append(f"[![Portfolio]({url})]({blog})")

    # Custom Social Links from request.social_links
    for link in social_links:
        details = SOCIAL_BADGE_MAP.get(link.platform)
        if details:
            bg, logo = details
            badge_url = f"https://img.shields.io/badge/{quote_plus(link.platform)}-{bg}?style=flat&logo={logo}&logoColor=white"
            badges.append(f"[![{link.platform}]({badge_url})]({link.url})")

    if not badges:
        return ""

    return connect_text + " ".join(badges)

def build_score_section(profile_score : int, collaboration_badge : str, include : bool) -> str:
    if not include:
        return ""
    
    score_badge = f"![Profile Score](https://img.shields.io/badge/Profile%20Score-{profile_score}%2F100-7851A9)"
    collab_badge = f"![Collaboration](https://img.shields.io/badge/Status-{quote_plus(collaboration_badge)}-2ea043)"
    
    return f"{score_badge} {collab_badge}"


def generate_readme(username: str, request: ReadmeRequest) -> str:
    
    # (Typing SVG)
    header = build_header(username, request.role, request.open_to_work)
    
    # 2. Tech Stack Section
    tech_stack = build_language_badges(request.tech_stack, request.include_language_badges)
    
    # 3. Stats Section 
    stats_streak = build_stats_and_streak(
        username, 
        request.theme, 
        request.include_stats_card, 
        request.include_streak_card
    )
    
    # 4. Featured Projects
    projects = build_repo_cards(
        username, 
        request.top_repos, 
        request.theme, 
        request.include_repo_cards
    )
    
    # 5. GitPulse Metrics (Score and Badge)
    metrics = build_score_section(
        request.profile_score, 
        request.collaboration_badge, 
        request.include_score_badges
    )
    
    # 6. Social Links
    socials = build_social_links(
        request.twitter, 
        request.blog, 
        request.social_links, 
        request.include_social_links
    )

    # Assembly with clean dividers and spacing

    final_sections = [
        header,
        f"<p align='center'>\n {tech_stack}\n</p>" if tech_stack else "",
        "---",
        stats_streak,
        projects,
        "---",
        socials
    ]
    
    return "\n\n".join([s for s in final_sections if s.strip()])   # Filter out empty strings and join