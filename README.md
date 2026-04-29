# SINTEF Deep Tech & Skill Radar

Map your research interests, expertise, and collaboration goals across deep tech areas — visualised as a group skill radar. Discover who you can build deep tech with, and let AI surface concrete collaboration opportunities.

---

## What It Does

| Feature | Description |
|---|---|
| **Submit Profile** | Each researcher rates their interest and expertise (0–5) across 30 deep tech areas, sets collaboration goals, and describes their current research focus |
| **Team Radar** | Recharts radar chart showing average interest and expertise across the whole team, filterable by individual members |
| **Find Collaborators** | Client-side synergy scoring surfaces researchers with overlapping areas; optional AI deep analysis uses GPT to generate concrete collaboration suggestions |
| **All Profiles** | Searchable table of all submissions with expandable rows, CSV export, and admin data wipe |

---

## Architecture

```
Browser (React 18 + Vite)
        │  /api/*  (dev: Vite proxy → :8000, prod: same origin)
        ▼
FastAPI (server.py)  ←→  SQLite (data/profiles.db)
        │
        └── OpenAI API (optional, for AI synergy endpoint)
```

**Stack:**

- **Frontend**: React 18, Vite, Recharts, custom CSS design system (no framework)
- **Backend**: FastAPI, Uvicorn, Pydantic v2
- **Storage**: SQLite with WAL mode, additive migrations, UPSERT on name
- **AI**: OpenAI Python SDK v2, `gpt-4o-mini` by default (configurable)
- **Deployment**: Docker multi-stage build (Node → Python slim)

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.11+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | ships with Node |
| Docker + Docker Compose | any recent | for container deployment |
| OpenAI API key | — | optional; enables AI synergy |

---

## Local Development

Two terminals.

**Terminal 1 — Python backend:**

```bash
cd /path/to/Deep_techradar
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Optional: create a .env file
echo "OPENAI_API_KEY=sk-..." > .env

python server.py               # runs on http://localhost:8000
```

**Terminal 2 — React frontend (dev server with hot reload):**

```bash
cd /path/to/Deep_techradar/frontend
npm install
npm run dev                    # runs on http://localhost:5173
```

Open **http://localhost:5173** in your browser. API calls are proxied to port 8000 automatically via the Vite config.

> **Note:** The backend serves the built frontend in production (Docker). In local dev, the Vite dev server handles the frontend with hot reload.

---

## Running & Sharing with ngrok

The app runs locally via Docker and is shared publicly over HTTPS using [ngrok](https://ngrok.com). No cloud hosting account needed — ngrok creates a secure tunnel from a public URL to your machine.

### First-time setup

**1. Install ngrok (ARM64 / aarch64):**

```bash
curl -Lo /tmp/ngrok.tgz https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz
tar -xzf /tmp/ngrok.tgz -C /tmp
mkdir -p ~/.local/bin && mv /tmp/ngrok ~/.local/bin/ngrok
# Add ~/.local/bin to your PATH if not already there
```

For x86-64 Linux, replace `arm64` with `amd64` in the URL.

**2. Add your ngrok auth token to `.env`:**

```bash
# .env
NGROK_AUTHTOKEN=your-token-here   # from https://dashboard.ngrok.com/authtokens
```

### Start everything

```bash
docker compose up --build -d
```

This starts two containers:
- `deep-techradar` — the FastAPI + React app
- `deep-techradar-ngrok` — the ngrok tunnel (HTTPS, public URL)

### Get the public URL

```bash
./url.sh
# → https://xxxxxxxx.ngrok-free.app
```

Or open **http://localhost:4040** in your browser for the ngrok dashboard (live traffic, URL, inspection).

Share the printed URL with anyone — it works from any browser, no VPN needed, HTTPS is automatic.

### Useful commands

```bash
docker compose logs -f ngrok        # stream ngrok tunnel logs
docker compose logs -f app          # stream app logs
docker compose down                 # stop everything
docker compose up --build -d        # rebuild after code changes
./url.sh                            # print current public URL
```

> **Note:** The free ngrok tier gives a new random URL each time you restart. To get a fixed URL, upgrade to a paid ngrok plan and add `--domain your-domain.ngrok.app` to the `command` in `docker-compose.yml`.

### Data persistence

The SQLite database lives at `./data/profiles.db` on your machine. It survives restarts and rebuilds. Back it up:

```bash
cp data/profiles.db data/profiles.backup.$(date +%Y%m%d).db
```

---

## Environment Variables

Create a `.env` file in the project root (next to `server.py`).

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | No | — | OpenAI API key. If absent, the "Deep AI Analysis" button is hidden |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Any OpenAI chat model that supports JSON response format |
| `NGROK_AUTHTOKEN` | Yes (for sharing) | — | ngrok auth token from dashboard.ngrok.com/authtokens |

The app works fully without an OpenAI key — AI features are simply hidden.

---

## Configuration (`config.py`)

All team and domain configuration lives in [config.py](config.py). Edit this file to customise the app for your team.

### Adding team members

```python
TEAM_MEMBERS: list[str] = [
    "Sagar Sen",
    "Merve Astekin",
    # ... add names here
    "Your New Colleague",
]
```

Names appear in the "Select your name" dropdown on the Submit Profile page.

### Adding Scholar profile links

```python
SCHOLAR_URL_MAP: dict[str, str] = {
    "Your New Colleague": "https://scholar.google.com/citations?user=XXXX",
}
```

### Adding or removing tech areas

```python
EXTENDED_TECH_AREAS: list[str] = [
    "AI/ML & Trustworthy AI",
    "IoT & Edge Computing",
    # ... 30 areas total
    "Your New Area",
]
```

Areas appear as checkboxes on the Submit Profile page and as axes on the Team Radar.

### Collaboration goal options

```python
COLLAB_GOALS: list[str] = [
    "Research",
    "Paper Writing",
    "Prototyping",
    "Grant / Funding Proposal",
    "Teaching / Mentoring",
    "Open Source Project",
]
```

---

## API Reference

Base URL: `http://localhost:8000` (local dev) or your deployed URL.

Interactive docs: **`/api/docs`**

---

### `GET /api/health`

Health check.

**Response:**
```json
{ "status": "ok" }
```

---

### `GET /api/config`

Returns app configuration needed by the frontend.

**Response:**
```json
{
  "app_title":    "SINTEF Deep Tech & Skill Radar",
  "app_subtitle": "...",
  "team_members": ["Sagar Sen", "Merve Astekin", "..."],
  "tech_areas":   ["AI/ML & Trustworthy AI", "IoT & Edge Computing", "..."],
  "collab_goals": ["Research", "Paper Writing", "..."],
  "has_openai":   true
}
```

---

### `GET /api/profiles`

Returns all submitted profiles, ordered newest first.

**Response:** Array of profile objects (see Profile Data Model below).

---

### `GET /api/profiles/{name}`

Returns a single profile by exact name.

**Response:** Profile object, or `404` if not found.

---

### `POST /api/profiles`

Submit or update a profile (upsert on `name`).

**Request body:**
```json
{
  "name":         "Karthik Shivashankar",
  "org":          "SINTEF",
  "areas":        ["AI/ML & Trustworthy AI", "IoT & Edge Computing"],
  "interests":    { "AI/ML & Trustworthy AI": 5, "IoT & Edge Computing": 3 },
  "expertise":    { "AI/ML & Trustworthy AI": 4, "IoT & Edge Computing": 2 },
  "collab_goals": ["Research", "Prototyping"],
  "description":  "Currently working on energy-efficient AI at the edge."
}
```

All fields except `name` are optional and default to empty.

**Response:** `201 Created` — `{ "status": "ok" }`

---

### `DELETE /api/profiles`

Wipes all profiles. Password protected.

**Request body:**
```json
{ "password": "sintef2024" }
```

**Response:** `{ "status": "ok" }` or `403` on wrong password.

---

### `POST /api/synergy`

AI-powered collaboration analysis using OpenAI. Returns researchers with synergy scores and concrete collaboration suggestions. Requires `OPENAI_API_KEY` to be set.

**Request body:**
```json
{
  "areas":       ["AI/ML & Trustworthy AI", "Federated Learning"],
  "search_text": "privacy-preserving edge inference"
}
```

**Response:**
```json
{
  "results": [
    {
      "name":                     "Sagar Sen",
      "synergy_score":            82,
      "shared_areas":             ["AI/ML & Trustworthy AI"],
      "complementary_areas":      ["Formal Methods & Verification"],
      "shared_interests_summary": "Both work at the intersection of trustworthy AI and embedded systems...",
      "collaboration_suggestions": [
        "Co-author a paper on formally verified TinyML pipelines",
        "Build a privacy-preserving anomaly detection prototype for IIoT"
      ],
      "deep_tech_areas_to_explore": ["Federated Learning", "Privacy Engineering"]
    }
  ],
  "summary": "Two researchers share strong overlap in edge AI and privacy..."
}
```

Only profiles with `synergy_score >= 25` are returned, sorted descending.

---

## Profile Data Model

| Field | Type | Description |
|---|---|---|
| `name` | string | Unique identifier — must match a name in `TEAM_MEMBERS` |
| `org` | string | Organisation / department |
| `timestamp` | string | ISO 8601 UTC, set automatically on save |
| `areas` | string[] | Tech areas the person has rated |
| `interests` | object | `{ "area": 0–5 }` — how interested they are |
| `expertise` | object | `{ "area": 0–5 }` — how expert they are |
| `collab_goals` | string[] | What kinds of collaboration they want |
| `description` | string | Current research focus / collaboration idea |

Rating scale: `0` = not rated / N/A, `1` = beginner, `5` = expert / very interested.

---

## Frontend Components

```
frontend/src/
├── App.jsx                  Root — loads config, manages tabs, hero stats
├── App.css                  Full design system (tokens, components, layout)
├── api.js                   All fetch calls to the backend
└── components/
    ├── SubmitProfile.jsx    Profile form — area selection, sliders, collab goals
    ├── TeamRadar.jsx        Recharts RadarChart with member filter pills
    ├── FindCollaborators.jsx Synergy finder — local scoring + AI mode
    ├── AllSubmissions.jsx   Data table with CSV export and admin tools
    └── TagInput.jsx         Reusable tag chip input (Enter or comma to add)
```

### Design tokens (App.css)

```css
--blue: #2563EB    --purple: #7C3AED   --cyan: #0891B2
--teal: #0D9488    --amber: #D97706    --muted: #94A3B8
--bg: #EDF1FA      --surface: #FFFFFF  --surface2: #F4F7FE
--r: 12px          --r-sm: 7px         --r-pill: 100px
--f: 'Inter'       --fc: 'Barlow Condensed'  --fm: 'JetBrains Mono'
```

### Synergy scoring (client-side, no server round-trip)

`FindCollaborators.jsx` scores profiles locally using `useMemo`:

| Signal | Points |
|---|---|
| Rated area match (interest or expertise ≥ threshold) | sum of both ratings |
| Complementary interest (wants to work on area in query) | +3 per area |
| Keyword match in free text fields | +1.5 per hit |

Profiles scoring below 1 are filtered out. Scores are normalised to 0–100% relative to the top scorer in the result set.

---

## Admin Operations

### Clear all profiles

From the **All Profiles** tab → scroll to **Danger Zone** → enter the admin password → click **Clear All Data**.

Password: `sintef2024`

To change the password, edit [server.py](server.py) line 16:
```python
ADMIN_PASSWORD = "sintef2024"
```

### Backup the database

```bash
cp data/profiles.db data/profiles.backup.$(date +%Y%m%d).db
```

### Inspect the database directly

```bash
sqlite3 data/profiles.db
.tables
SELECT name, timestamp FROM profiles ORDER BY timestamp DESC;
.quit
```

---

## OpenAI Integration

When `OPENAI_API_KEY` is set:

- The **"Deep AI Analysis"** button appears on the Find Collaborators tab
- Clicking it sends all profiles + the current query to `POST /api/synergy`
- The backend calls OpenAI with `response_format: json_object` and `temperature: 0.3`
- Model defaults to `gpt-4o-mini`; override with the `OPENAI_MODEL` env var
- Results are rendered as cards: synergy score bar, shared areas, complementary areas, a 1–2 sentence overlap summary, and 2–3 concrete what-to-build-together suggestions

The prompt explicitly instructs the model not to assign labels or types to people — only to describe areas, overlaps, and what could be built or published together.

Typical cost per analysis call: under $0.01 with `gpt-4o-mini` for a team of 13 profiles.

---

## Troubleshooting

**Port already in use**
```bash
lsof -i :8000
kill -9 <PID>
```

**Frontend shows blank page after Docker build**

Check that the Node build step succeeded:
```bash
docker compose logs | grep -i "dist\|error\|failed"
```

**"OpenAI not configured" or AI analysis fails**

Check that `OPENAI_API_KEY` is set and valid, and that `OPENAI_MODEL` names a model that supports `response_format: json_object`. Restart after changing env vars:
```bash
docker compose down && docker compose up -d
```

**Profile not appearing after submit**

Verify the backend is running:
```bash
curl http://localhost:8000/api/health
```

**New columns not appearing after schema change**

The `_init()` function in `storage.py` adds missing columns automatically on every startup via `ALTER TABLE`. Restart the server and it will self-migrate.

---

## Project Structure

```
Deep_techradar/
├── server.py              FastAPI app, all API routes
├── storage.py             SQLite persistence layer
├── config.py              Team members, tech areas, app title
├── requirements.txt       Python dependencies
├── Dockerfile             Multi-stage build (Node → Python slim)
├── docker-compose.yml     App + ngrok tunnel config
├── url.sh                 Print the current public ngrok URL
├── .env                   Local secrets (not committed)
├── data/
│   └── profiles.db        SQLite database (auto-created on first run)
└── frontend/
    ├── package.json
    ├── vite.config.js     Dev proxy: /api → localhost:8000
    ├── index.html
    └── src/
        ├── App.jsx
        ├── App.css
        ├── api.js
        └── components/
            ├── SubmitProfile.jsx
            ├── TeamRadar.jsx
            ├── FindCollaborators.jsx
            ├── AllSubmissions.jsx
            └── TagInput.jsx
```
