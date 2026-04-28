from app.schemas import ReadmeRequest,SocialLink
from app.lib.social_links import SOCIAL_BADGE_MAP
from app.lib.tech_stack import STACK_BADGE_MAP
from urllib.parse import quote_plus
from typing import Optional


#Helper function
def get_badge_details(name: str) -> Optional[tuple[str,str,str]]:
    """Searches nested STACK_BADGE_MAP for a tech name."""

    for category in STACK_BADGE_MAP.values():
        if name in category:
            return category[name]
    return None


def build_header(username: str, role: Optional[str], open_to_work: bool) -> str:
    base_url = "https://readme-typing-svg.demolab.com"

    lines = [] 
    if role:
        lines.append(quote_plus(role))      #special characters cannot be used directly in urls,hence apostrophe becomes %27 , comma becomes %2C and so on

    if open_to_work:
        lines.append(quote_plus("Available for Opportunities"))
    
    lines_param = ";".join(lines)     #New lines are seperated by ;

    return (
        f'<p align="center">\n'
        f'  <img src="{base_url}?font=Fira+Code&size=22&duration=3000&pause=1000&color=58A6FF&center=true&vCenter=true&width=600&lines={lines_param}" />\n'
        f'</p>'
    )

def build_about(bio_text: Optional[str], interests: Optional[str]) -> list[str]:
    """Bio paragraph and interests"""
    res = []
 
    if bio_text:
        res.append(f"### About Me\n\n{bio_text.strip()}")
 
    if interests:
        items = [interest.strip() for interest in interests.split(".") if interest.strip()]         #We'll ask user to split the points by fullstop
        formatted_interests = "\n".join([f"- {item}" for item in items])
        res.append(f"**Interests:**\n\n{formatted_interests}")

    return res


def build_language_badges(selected_stack: list[str], include: bool) -> str:
    if not include or not selected_stack:
        return ""
    
    all_category_sections = []     # We will collect badges grouped by their category for a better layout

    for category, items in STACK_BADGE_MAP.items():
        category_badges = []
        for name in items:
            if name in selected_stack:
                details = get_badge_details(name) 
                bg, logo, logo_color = details
                url = f"https://img.shields.io/badge/{quote_plus(name)}-{bg}?style=for-the-badge&logo={logo}&logoColor={logo_color}"
                category_badges.append(f'<img src="{url}" alt="{name}" height="35" />')   #height is best adjusted via <img> tags
        
        if category_badges:
            all_category_sections.append(f"**{category}:**\n" + " ".join(category_badges) + "\n")
            
    
    #if items are in selected_stack but not in our MAP
    unknown_badges = []
    mapped_names = [name for category in STACK_BADGE_MAP.values() for name in category]
    for name in selected_stack:
        if name not in mapped_names:
            url = f"https://img.shields.io/badge/{quote_plus(name)}-gray?style=for-the-badge"
            unknown_badges.append(f'<img src="{url}" alt="{name}" height="35" />')
    
    if unknown_badges:
        all_category_sections.append(" ".join(unknown_badges))

    badges_block = "\n<br />\n".join(all_category_sections)    # Join categories with a single newline or <br> for compact grouping
    return f"### Tech Stack\n\n{badges_block}"



def build_stats_and_streak(username: str, theme: str, include_stats: bool, include_streak: bool) -> str:
    if not (include_stats or include_streak):
        return ""
    
    stats_url = f"https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&theme={theme}&hide_border=true"
    streak_url = f"https://streak-stats.demolab.com/?user={username}&theme={theme}&hide_border=true"
    
    content = []
    if include_stats:
        content.append(f'<img src="{stats_url}" alt="Stats Card" height="175" />')
    if include_streak:
        content.append(f'<img src="{streak_url}" alt="Streak Card" height="175" />')
        
    return f'### GitHub Statistics\n\n<p align="center">\n' + "\n  ".join(content) + "\n</p>"


def build_repo_cards(username: str, top_repos: list[str], theme: str, include: bool) -> str:
    if not include or not top_repos:
        return ""
    
    base_url = "https://github-readme-stats.vercel.app/api/pin/"
    cards = [f'[![Repo]({base_url}?username={username}&repo={repo}&theme={theme})](https://github.com/{username}/{repo})' for repo in top_repos]
    
    # we'll use HTML table for reliable 2-column alignment (though it is an old concept)
    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i:i + 2]
        cells = "".join(f'<td width="50%" align="center">{c}</td>' for c in pair)
        rows.append(f"  <tr>{cells}</tr>")

    table = f'<table align="center" width="100%">\n' + "\n".join(rows) + "\n</table>"
    return f"###  Featured Projects\n\n{table}"


def build_social_links(twitter : Optional[str], blog : Optional[str], social_links  : list[SocialLink], include) -> str:
    if not include:
        return ""
    
    badges = []

    # Pre-filled Twitter
    if twitter:
        bg, logo = SOCIAL_BADGE_MAP.get("Twitter", ("1DA1F2", "twitter"))
        url = f"https://img.shields.io/badge/Twitter-{bg}?style=for-the-badge&logo={logo}&logoColor=white"
        badges.append(f'<a href="https://twitter.com/{twitter}"><img src="{url}" height = "35"/></a>')
    
    # Pre-filled Blog/Portfolio
    if blog:
        bg, logo = SOCIAL_BADGE_MAP.get("Portfolio", ("000000", "linktree"))
        url = f"https://img.shields.io/badge/Portfolio-{bg}?style=for-the-badge&logo={logo}&logoColor=white"
        badges.append(f'<a href="{blog}"><img src="{url}" height = "35"/></a>')

    # Custom Social Links from request.social_links
    for link in social_links:
        details = SOCIAL_BADGE_MAP.get(link.platform)
        if details:
            bg, logo = details
            badge_url = f"https://img.shields.io/badge/{quote_plus(link.platform)}-{bg}?style=for-the-badge&logo={logo}&logoColor=white"
            badges.append(f'<a href="{link.url}"><img src="{url}" height = "35"/></a>')

    if not badges:
        return ""

    return f"###  Let's Connect\n\n" + f'<p align="center">\n  {" &nbsp; ".join(badges)}\n</p>'    #join badges with a non-breaking space for horizontal flow


def build_score_section(profile_score : int, collaboration_badge : str, include : bool) -> str:
    if not include:
        return ""
    
    score_badge = f"![Profile Score](https://img.shields.io/badge/Profile%20Score-{profile_score}%2F100-7851A9)?style=for-the-badge"      # / is parsed as %2F
    collab_badge = f"![Collaboration](https://img.shields.io/badge/Status-{quote_plus(collaboration_badge)}-2ea043)?style=for-the-badge"
    
    return "### Profile Score \n\n" + f"{score_badge}   {collab_badge}"


def build_most_used_languages(username: str, theme: str, include: bool) -> str:
    """github-readme-stats top languages card """

    if not include:
        return ""
 
    url = f"https://github-readme-stats.vercel.app/api/top-langs/?username={username}&layout=compact&theme={theme}&hide_border=true&langs_count=8"

    return f'<div align = "center">\n\n<img height="160" src="{url}" alt="Most Used Languages" /></div>\n\n'


def build_profile_views(username: str, include: bool) -> str:
    """Profile view counter badge - Automatically increments when someone views the profile README."""

    if not include:
        return ""
 
    url = f"https://komarev.com/ghpvc/?username={username}&label=Profile+Views&color=58A6FF&style=for-the-badge"
    
    return f'<div align = "center">\n\n<img height="160" src="{url}" alt="Profile Views" />\n\n'


def build_fun_fact(fun_fact: Optional[str]) -> str:
    if not fun_fact:
        return ""
    return f"###  Fun Fact\n\n> {fun_fact.strip()}"     # > is for blockquote in  markdown 
 
 
def build_quote(quote: Optional[str]) -> str:
    if not quote:
        return ""
    return f"###  Quote I Live By\n\n> _{quote.strip()}_"

#Note:
#the markdown string in the response would look messy bcz of raw html tags and escape characters
# once that string is passed to a frontend component that understands markdown,it renders as a clean, formatted document

def generate_readme(username: str, request: ReadmeRequest) -> str:
    # 1. Typing SVG
    typing_header = build_header(username, request.role, request.open_to_work)

    # 2. About Me
    bio, interests = build_about(request.bio_text, request.interests)
    
    # 3. Tech Stack Section
    tech_stack = build_language_badges(request.tech_stack, request.include_language_badges)
    
    # 4. Stats Section 
    stats_streak = build_stats_and_streak(
        username, 
        request.theme, 
        request.include_stats_card, 
        request.include_streak_card
    )
    
    # 5. Most used languages card 
    top_languages = build_most_used_languages(
                username,
                request.theme,
                request.include_most_used_languages
            )

    # 6. Featured Projects
    projects = build_repo_cards(
        username, 
        request.top_repos, 
        request.theme, 
        request.include_repo_cards
    )

    # 7. GitPulse Metrics (Score and Badge)
    metrics = build_score_section(
        request.profile_score, 
        request.collaboration_badge, 
        request.include_score_badges
    )
    
    # 8. Profile views counter 
    profile_views = build_profile_views(username, request.include_profile_views)

    # 9. Social Links
    socials = build_social_links(
        request.twitter, 
        request.blog, 
        request.social_links, 
        request.include_social_links
    )

    # 10. Fun fact
    fun_fact  =  build_fun_fact(request.fun_fact)
 
    # 11. Quote 
    quote  =  build_quote(request.quote)

    # Assembly with clean dividers and spacing

    final_sections = [
        f"<h2> Hello, I'm {request.name} </h2>",
        typing_header,
        bio,
        f"<p align='center'>\n {tech_stack}\n</p>" if tech_stack else "",
        "---",
        stats_streak,
        top_languages,
        "---",
        projects,
        interests,
        metrics,
        profile_views,
        "---",
        socials,
        fun_fact,
        quote
    ]
    
    return "\n\n".join([s for s in final_sections if s and str(s).strip()])   # Filter out empty strings and join
