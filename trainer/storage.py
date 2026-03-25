import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from django.conf import settings

COOKIE_NAME = "trainer_uid"


def _data_dir() -> Path:
    base = Path(settings.BASE_DIR) / "data" / "users"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_or_create_user_id(cookie_value: Optional[str]) -> str:
    if not cookie_value:
        return str(uuid.uuid4())
    try:
        uuid.UUID(cookie_value)
        return cookie_value
    except ValueError:
        return str(uuid.uuid4())


def _path_for_user(user_id: str) -> Path:
    return _data_dir() / f"{user_id}.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


DEFAULT_PROFILE: dict[str, Any] = {
    "version": 1,
    "nickname": "",
    "settings": {
        "allow_addition": True,
        "allow_subtraction": True,
        "allow_multiplication": True,
    },
    "stats": {
        "level": 1,
        "correct_streak": 0,
        "total_attempts": 0,
        "total_correct": 0,
    },
    "attempts": [],
}


def load_profile(user_id: str) -> dict[str, Any]:
    path = _path_for_user(user_id)
    if not path.exists():
        return json.loads(json.dumps(DEFAULT_PROFILE))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return json.loads(json.dumps(DEFAULT_PROFILE))

    merged = json.loads(json.dumps(DEFAULT_PROFILE))
    merged.update({k: v for k, v in data.items() if k in merged})
    merged["settings"].update(data.get("settings", {}))
    merged["stats"].update(data.get("stats", {}))
    if isinstance(data.get("attempts"), list):
        merged["attempts"] = data["attempts"]
    return merged


def save_profile(user_id: str, profile: dict[str, Any]) -> None:
    path = _path_for_user(user_id)
    tmp = path.with_suffix(".json.tmp")
    payload = json.dumps(profile, ensure_ascii=False, indent=2)
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(path)


def update_profile(
    user_id: str, *, nickname: str, settings_dict: dict[str, Any]
) -> dict[str, Any]:
    profile = load_profile(user_id)
    profile["nickname"] = nickname.strip()
    profile["settings"].update(settings_dict)
    save_profile(user_id, profile)
    return profile
