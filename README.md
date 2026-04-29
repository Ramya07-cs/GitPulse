# GitPulse

A GitHub profile analyzer that fetches your repos, events and stats,
scores your activity and generates a fully customized README.md —
ready to download and drop into your profile repo.

## Live API

**Base URL:**  [`https:/gitpulse-0bi1.onrender.com`](https://gitpulse-0bi1.onrender.com)

**Swagger UI:** [`https://gitpulse-0bi1.onrender.com/docs`](https://gitpulse-0bi1.onrender.com/docs)
(At this stage, both urls land on the page)

# Tech Stack
 
**Backend:** `FastAPI · Python · Pydantic · HTTPX · asyncio` 

**Deploy:** Render  
**Data source:** GitHub REST API (authenticated — 5000 req/hour)
 

## Project status

**`Backend API`** - Live on Render

**`Swagger/Redoc`** - Available

**`Frontend (React + Vite)`** - In progress

# Try it out

**Frontend is currently under development.** In the meantime, you can explore and test all API endpoints directly via the interactive Swagger UI below.

Open Swagger UI at **https://gitpulse-0bi1.onrender.com/docs** — every endpoint is documented and testable directly in the browser with no setup.
 
**`Quick test — analyse any GitHub user:`**

Fetches and analyses a GitHub profile in detail.

1. Go to `/user/{username}/dashboard` endpoint → click **Try it out**
2. Enter a username (e.g. `torvalds`, `gaearon`, your own)
3. Click **Execute** — the full analysis returns as JSON

#### Note :
- The response includes profile card, a stats row, a profile strength score with actionable tips, language breakdown by percentage, repo quality scores, a collaboration badge, an activity heatmap, and a recent event feed — all derived from three parallel API calls.
- `Most_active_hour` is in UTC time . The hours in heatmap are also in UTC. 
- The github restapi only returns the events of past 30 days, so if the user has been inactive for a while, the events array may be empty. This is expected behaviour.Hence we may shift to graphql api in the future to get around this limitation and fetch more historical events.
---

**`Generate a README:`**

Generates a fully customized GitHub profile `README.md` in markdown format, based on the dashboard data and your personal preferences.

Use the `POST /user/{username}/readme` endpoint. 

Example request body: 
```json
{
  "name": "Linus Torvalds",
  "bio_text": "I like Linux and Git. You may have heard of them.",
  "top_repos": ["linux", "test-tlb", "GuitarPedal"],
  "primary_languages": ["C", "OpenSCAD"],
  "profile_score": 60,
  "collaboration_badge": "Solo developer",
  "interests": "OS development, version control, scuba diving",
  "tech_stack": ["Linux", "Git", "C", "Bash"],
  "role": "Creator of Linux & Git",
  "open_to_work": false,
  "fun_fact": "I accidentally created Git in two weeks.",
  "quote": "Make moves in silence.Let success make the noise",
  "twitter": null,
  "blog": null,
  "social_links": [
    { "platform": "LinkedIn", "url": "https://linkedin.com/in/" }
  ],
  "theme": "dark",
  "include_stats_card": true,
  "include_streak_card": true,
  "include_repo_cards": true,
  "include_language_badges": true,
  "include_social_links": true,
  "include_score_badges": true,
  "include_most_used_languages": true,
  "include_profile_views": true
}
```

#### Note:
- `Colloboration badge` is determined by the backend based on your contribution patterns. It can be "Top Contibutor", "Active Collaborator", "Building Momentum" or "Solo Developer".
- `theme` can be "dark", "default", "rose", "blue_navy", "github_dark" or "midnight-purple" — it controls the styling of your generated README cards.This is made available as a dropdown in the frontend UI.
- The response contains a `markdown` field which contains the full generated `README.md` as a raw string. It may look messy or hard to read in its raw form (lots of `\n`,`\"` escape sequences, badge URLs, etc.) — this is expected. The frontend will render it correctly into a clean, formatted preview once it's live.

---

# Project Structure
 
```
backend/
├── main.py                  # FastAPI app, routes
├── app/
│   ├── github_client.py     # GitHub API calls 
│   ├── schemas.py           # Pydantic models for all request/response shapes
│   ├── lib/
│   │   ├── tech_stack.py    
│   │   └── social_links.py  
│   └── utils/
│       ├── repo_utils.py    # Language breakdown, quality scoring, top repos
│       ├── event_utils.py   # Activity & heatmap analysis
│       ├── score_utils.py   # Profile & collaboration scoring
│       └── readme_utils.py  # README generation logic
└── requirements.txt
```
