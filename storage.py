import json
from datetime import datetime, timezone
from functools import lru_cache

import pandas as pd
from datasets import Dataset, load_dataset
from huggingface_hub import HfApi

import config

_SCHEMA_COLS = [
    "name", "org", "timestamp",
    "areas_json", "interests_json", "expertise_json",
    "collab_goals_json", "description",
]

_EMPTY_ROW: dict[str, list] = {col: [] for col in _SCHEMA_COLS}


@lru_cache(maxsize=1)
def _hf_username() -> str:
    if config.HF_USERNAME:
        return config.HF_USERNAME
    api = HfApi(token=config.HF_TOKEN)
    return api.whoami()["name"]


def _repo_id() -> str:
    return f"{_hf_username()}/{config.HF_DATASET_NAME}"


def _repo_exists() -> bool:
    api = HfApi(token=config.HF_TOKEN)
    try:
        api.dataset_info(_repo_id())
        return True
    except Exception:
        return False


def get_or_create_dataset() -> Dataset:
    if _repo_exists():
        return load_dataset(_repo_id(), split="train", token=config.HF_TOKEN)
    ds = Dataset.from_dict(_EMPTY_ROW)
    ds.push_to_hub(_repo_id(), token=config.HF_TOKEN)
    return ds


def save_profile(profile: dict) -> None:
    """Upsert profile — one entry per user, update if already exists."""
    name = profile.get("name", "")
    row = {
        "name":              name,
        "org":               profile.get("org", ""),
        "timestamp":         datetime.now(timezone.utc).isoformat(),
        "areas_json":        json.dumps(profile.get("areas", [])),
        "interests_json":    json.dumps(profile.get("interests", {})),
        "expertise_json":    json.dumps(profile.get("expertise", {})),
        "collab_goals_json": json.dumps(profile.get("collab_goals", [])),
        "description":       profile.get("description", ""),
    }
    try:
        existing = load_dataset(_repo_id(), split="train", token=config.HF_TOKEN)
        df = existing.to_pandas()
        df = df[df["name"] != name].reset_index(drop=True)
        new_row_df = pd.DataFrame([row])
        df = pd.concat([df, new_row_df], ignore_index=True)
        df = df.reindex(columns=_SCHEMA_COLS, fill_value="")
        updated = Dataset.from_pandas(df, preserve_index=False)
    except Exception:
        updated = Dataset.from_dict({k: [v] for k, v in row.items()})
    updated.push_to_hub(_repo_id(), token=config.HF_TOKEN)


def get_profile_by_name(name: str) -> dict | None:
    """Return parsed profile dict for a user, or None if not found."""
    try:
        df = load_all_profiles()
        rows = df[df["name"] == name]
        if rows.empty:
            return None
        row = rows.iloc[0]
        return {
            "name":         row["name"],
            "org":          row.get("org", ""),
            "areas":        json.loads(row["areas_json"])        if isinstance(row["areas_json"],        str) else [],
            "interests":    json.loads(row["interests_json"])    if isinstance(row["interests_json"],    str) else {},
            "expertise":    json.loads(row["expertise_json"])    if isinstance(row["expertise_json"],    str) else {},
            "collab_goals": json.loads(row["collab_goals_json"]) if isinstance(row["collab_goals_json"], str) else [],
            "description":  row.get("description", ""),
        }
    except Exception:
        return None


def load_all_profiles() -> pd.DataFrame:
    """Pull latest dataset from HF Hub and return as DataFrame."""
    try:
        ds = load_dataset(_repo_id(), split="train", token=config.HF_TOKEN)
        return ds.to_pandas()
    except Exception:
        return pd.DataFrame(columns=_SCHEMA_COLS)


def clear_all_profiles() -> None:
    """Replace the HF dataset with an empty schema (wipes all profiles)."""
    _hf_username.cache_clear()
    ds = Dataset.from_dict(_EMPTY_ROW)
    ds.push_to_hub(_repo_id(), token=config.HF_TOKEN)
