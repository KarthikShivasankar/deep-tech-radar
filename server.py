import json
import os
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
import storage

ADMIN_PASSWORD = "sintef2024"
DIST = Path(__file__).parent / "frontend" / "dist"

app = FastAPI(title=config.APP_TITLE, docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProfileIn(BaseModel):
    name: str
    org: str = ""
    areas: list[str] = []
    interests: dict[str, int] = {}
    expertise: dict[str, int] = {}
    collab_goals: list[str] = []
    description: str = ""
    deep_tech_contribution: str = ""
    deep_tech_examples: str = ""


class AdminAction(BaseModel):
    password: str


class AskRequest(BaseModel):
    question: str


# ── API ────────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/config")
def get_config():
    return {
        "app_title":    config.APP_TITLE,
        "app_subtitle": config.APP_SUBTITLE,
        "team_members": config.TEAM_MEMBERS,
        "tech_areas":   config.EXTENDED_TECH_AREAS,
        "collab_goals": config.COLLAB_GOALS,
    }


@app.get("/api/profiles")
def get_all_profiles():
    return storage.load_all_profiles()


@app.get("/api/profiles/{name}")
def get_profile(name: str):
    p = storage.get_profile_by_name(name)
    if p is None:
        raise HTTPException(404, "Profile not found")
    return p


@app.post("/api/profiles", status_code=201)
def save_profile(profile: ProfileIn):
    storage.save_profile(profile.model_dump())
    return {"status": "ok"}


@app.delete("/api/profiles")
def clear_profiles(action: AdminAction):
    if action.password != ADMIN_PASSWORD:
        raise HTTPException(403, "Wrong password")
    storage.clear_all_profiles()
    return {"status": "ok"}


@app.post("/api/ask")
async def ask_question(req: AskRequest):
    """Stream a natural-language answer from Ollama about the team's profile data."""
    if not req.question.strip():
        raise HTTPException(400, "Question cannot be empty")

    profiles = storage.load_all_profiles()
    if not profiles:
        async def _empty():
            yield "No profiles have been submitted yet — ask team members to fill in their profiles first."
        return StreamingResponse(_empty(), media_type="text/plain; charset=utf-8")

    def _profile_text(p: dict) -> str:
        lines = [f"Name: {p['name']} | Org: {p.get('org', 'SINTEF')}"]
        if p.get("areas"):
            lines.append(f"  Active areas: {', '.join(p['areas'])}")
            rated = {a: (p["interests"].get(a, 0), p["expertise"].get(a, 0)) for a in p["areas"]}
            lines.append("  Ratings (interest/expertise): " +
                         ", ".join(f"{a} {i}/{e}" for a, (i, e) in rated.items()))
        if p.get("collab_goals"):
            lines.append(f"  Open to: {', '.join(p['collab_goals'])}")
        if p.get("description"):
            lines.append(f"  Current work: {p['description']}")
        if p.get("deep_tech_contribution"):
            lines.append(f"  Deep tech contribution: {p['deep_tech_contribution']}")
        if p.get("deep_tech_examples"):
            lines.append(f"  Deep tech examples: {p['deep_tech_examples']}")
        return "\n".join(lines)

    profiles_text = "\n\n".join(_profile_text(p) for p in profiles)

    system_prompt = (
        "You are an AI assistant helping a research group understand their team's "
        "deep tech expertise and collaboration opportunities. "
        "Below is the complete profile data for all team members. "
        "Answer questions concisely and specifically, citing names and facts from the data. "
        "If a question cannot be answered from the data, say so clearly.\n\n"
        f"TEAM PROFILES:\n{profiles_text}"
    )

    async def stream_ollama():
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{config.OLLAMA_HOST}/api/chat",
                    json={
                        "model":    config.OLLAMA_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user",   "content": req.question},
                        ],
                        "stream": True,
                    },
                ) as resp:
                    if resp.status_code != 200:
                        yield f"[Error] Ollama returned HTTP {resp.status_code}"
                        return
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            if content := data.get("message", {}).get("content", ""):
                                yield content
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            pass
        except httpx.ConnectError:
            yield f"[Error] Could not connect to Ollama at {config.OLLAMA_HOST}. Is Ollama running?"
        except Exception as exc:
            yield f"[Error] {exc}"

    return StreamingResponse(stream_ollama(), media_type="text/plain; charset=utf-8")


# ── Serve built React frontend ─────────────────────────────────────────────────

if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        return FileResponse(DIST / "index.html")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
