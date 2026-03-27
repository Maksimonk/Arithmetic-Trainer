"""
Генерация арифметических примеров по профилю пользователя (уровень и выбранные операции).
"""
import random
from typing import Any


def allowed_operations(profile: dict[str, Any]) -> list[str]:
    settings_dict = profile.get("settings", {})
    ops: list[str] = []
    if settings_dict.get("allow_addition", True):
        ops.append("+")
    if settings_dict.get("allow_subtraction", True):
        ops.append("-")
    if settings_dict.get("allow_multiplication", True):
        ops.append("×")
    return ops or ["+"]


def level_from_profile(profile: dict[str, Any]) -> int:
    try:
        return max(1, int(profile.get("stats", {}).get("level", 1)))
    except (TypeError, ValueError):
        return 1


def ranges_for_level(level: int, operation: str) -> tuple[int, int]:
    if operation == "×":
        max_val = min(12 + (level - 1) * 3, 99)
        return 0, max_val
    max_val = min(10 + (level - 1) * 10, 10_000)
    return 0, max_val


def generate_problem(profile: dict[str, Any]) -> dict[str, Any]:
    ops = allowed_operations(profile)
    op = random.choice(ops)
    level = level_from_profile(profile)
    lo, hi = ranges_for_level(level, op)
    left = random.randint(lo, hi)
    right = random.randint(lo, hi)
    if op == "-" and right > left:
        left, right = right, left
    return {"left": left, "right": right, "operation": op, "level": level}


def correct_answer(left: int, right: int, operation: str) -> int:
    if operation == "+":
        return left + right
    if operation == "-":
        return left - right
    return left * right
