import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "profiles.db"
DB_PATH.parent.mkdir(exist_ok=True)

_DDL = """
CREATE TABLE IF NOT EXISTS profiles (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    name                  TEXT UNIQUE NOT NULL,
    org                   TEXT DEFAULT '',
    timestamp             TEXT DEFAULT '',
    areas_json            TEXT DEFAULT '[]',
    interests_json        TEXT DEFAULT '{}',
    expertise_json        TEXT DEFAULT '{}',
    collab_goals_json     TEXT DEFAULT '[]',
    description           TEXT DEFAULT '',
    deep_tech_contribution TEXT DEFAULT '',
    deep_tech_examples    TEXT DEFAULT ''
)
"""

_MIGRATE_ADD = [
    ("deep_tech_contribution", "TEXT DEFAULT ''"),
    ("deep_tech_examples",     "TEXT DEFAULT ''"),
]

_MIGRATE_DROP = [
    "custom_areas_json",
    "research_areas_json",
    "deep_tech_interests_json",
]


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def _init():
    with _conn() as c:
        c.execute(_DDL)
        for col, defn in _MIGRATE_ADD:
            try:
                c.execute(f"ALTER TABLE profiles ADD COLUMN {col} {defn}")
            except Exception:
                pass
        for col in _MIGRATE_DROP:
            try:
                c.execute(f"ALTER TABLE profiles DROP COLUMN {col}")
            except Exception:
                pass


_init()


def save_profile(profile: dict) -> None:
    name = profile.get("name", "")
    with _conn() as c:
        c.execute(
            """
            INSERT INTO profiles
                (name, org, timestamp,
                 areas_json, interests_json, expertise_json, collab_goals_json,
                 description, deep_tech_contribution, deep_tech_examples)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(name) DO UPDATE SET
                org=excluded.org,
                timestamp=excluded.timestamp,
                areas_json=excluded.areas_json,
                interests_json=excluded.interests_json,
                expertise_json=excluded.expertise_json,
                collab_goals_json=excluded.collab_goals_json,
                description=excluded.description,
                deep_tech_contribution=excluded.deep_tech_contribution,
                deep_tech_examples=excluded.deep_tech_examples
            """,
            (
                name,
                profile.get("org", ""),
                datetime.now(timezone.utc).isoformat(),
                json.dumps(profile.get("areas", [])),
                json.dumps(profile.get("interests", {})),
                json.dumps(profile.get("expertise", {})),
                json.dumps(profile.get("collab_goals", [])),
                profile.get("description", ""),
                profile.get("deep_tech_contribution", ""),
                profile.get("deep_tech_examples", ""),
            ),
        )


def get_profile_by_name(name: str) -> dict | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM profiles WHERE name=?", (name,)).fetchone()
    return _parse(dict(row)) if row else None


def load_all_profiles() -> list[dict]:
    with _conn() as c:
        rows = c.execute("SELECT * FROM profiles ORDER BY timestamp DESC").fetchall()
    return [_parse(dict(r)) for r in rows]


def clear_all_profiles() -> None:
    with _conn() as c:
        c.execute("DELETE FROM profiles")


def _parse(row: dict) -> dict:
    def _j(v, d):
        try:
            return json.loads(v) if v else d
        except Exception:
            return d

    return {
        "name":                  row["name"],
        "org":                   row.get("org", ""),
        "timestamp":             row.get("timestamp", ""),
        "areas":                 _j(row.get("areas_json"),         []),
        "interests":             _j(row.get("interests_json"),     {}),
        "expertise":             _j(row.get("expertise_json"),     {}),
        "collab_goals":          _j(row.get("collab_goals_json"),  []),
        "description":           row.get("description", ""),
        "deep_tech_contribution": row.get("deep_tech_contribution", ""),
        "deep_tech_examples":    row.get("deep_tech_examples", ""),
    }
