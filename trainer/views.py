from typing import Any, Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import AnswerForm, SettingsForm
from .problem import correct_answer, generate_problem
from .storage import COOKIE_NAME, get_or_create_user_id, load_profile, save_profile, update_profile, utc_now_iso


def _with_uid_cookie(response: HttpResponse, user_id: str) -> HttpResponse:
    response.set_cookie(COOKIE_NAME, user_id, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return response


def home(request: HttpRequest) -> HttpResponse:
    user_id = get_or_create_user_id(request.COOKIES.get(COOKIE_NAME))
    profile = load_profile(user_id)
    stats = profile.get("stats", {})
    nickname = (profile.get("nickname") or "").strip() or "Гость"
    context = {
        "nickname": nickname,
        "level": stats.get("level", 1),
        "total_attempts": stats.get("total_attempts", 0),
        "total_correct": stats.get("total_correct", 0),
        "correct_streak": stats.get("correct_streak", 0),
    }
    response = render(request, "trainer/home.html", context)
    return _with_uid_cookie(response, user_id)


def settings_view(request: HttpRequest) -> HttpResponse:
    user_id = get_or_create_user_id(request.COOKIES.get(COOKIE_NAME))
    profile = load_profile(user_id)

    if request.method == "POST":
        form = SettingsForm(request.POST)
        if form.is_valid():
            update_profile(
                user_id,
                nickname=form.cleaned_data["nickname"],
                settings_dict={
                    "allow_addition": bool(form.cleaned_data.get("allow_addition")),
                    "allow_subtraction": bool(form.cleaned_data.get("allow_subtraction")),
                    "allow_multiplication": bool(form.cleaned_data.get("allow_multiplication")),
                },
            )
            return redirect(reverse("home"))
    else:
        initial = {
            "nickname": profile.get("nickname", ""),
            **profile.get("settings", {}),
        }
        form = SettingsForm(initial=initial)

    response = render(request, "trainer/settings.html", {"form": form})
    return _with_uid_cookie(response, user_id)


def train(request: HttpRequest) -> HttpResponse:
    user_id = get_or_create_user_id(request.COOKIES.get(COOKIE_NAME))
    profile = load_profile(user_id)
    feedback: Optional[dict[str, Any]] = None

    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            left = form.cleaned_data["left"]
            right = form.cleaned_data["right"]
            operation = form.cleaned_data["operation"]
            user_answer = form.cleaned_data["answer"]
            corr = correct_answer(left, right, operation)
            is_correct = user_answer == corr

            stats_dict = profile.setdefault("stats", {})
            stats_dict["total_attempts"] = int(stats_dict.get("total_attempts", 0)) + 1
            if is_correct:
                stats_dict["total_correct"] = int(stats_dict.get("total_correct", 0)) + 1
                stats_dict["correct_streak"] = int(stats_dict.get("correct_streak", 0)) + 1
            else:
                stats_dict["correct_streak"] = 0

            streak = int(stats_dict.get("correct_streak", 0))
            if streak and streak % 5 == 0:
                stats_dict["level"] = int(stats_dict.get("level", 1)) + 1

            attempt = {
                "ts": utc_now_iso(),
                "level": int(stats_dict.get("level", 1)),
                "left": left,
                "right": right,
                "operation": operation,
                "user_answer": user_answer,
                "correct_answer": corr,
                "is_correct": is_correct,
            }
            profile.setdefault("attempts", []).insert(0, attempt)
            profile["attempts"] = profile["attempts"][:200]
            save_profile(user_id, profile)

            feedback = {
                "is_correct": is_correct,
                "correct_answer": corr,
                "expression": f"{left} {operation} {right}",
            }
            profile = load_profile(user_id)

    problem = generate_problem(profile)
    form = AnswerForm(
        initial={
            "left": problem["left"],
            "right": problem["right"],
            "operation": problem["operation"],
        }
    )
    nickname = (profile.get("nickname") or "").strip() or "Гость"
    stats = profile.get("stats", {})
    response = render(
        request,
        "trainer/train.html",
        {
            "form": form,
            "problem": problem,
            "feedback": feedback,
            "nickname": nickname,
            "stats": stats,
        },
    )
    return _with_uid_cookie(response, user_id)


def history(request: HttpRequest) -> HttpResponse:
    user_id = get_or_create_user_id(request.COOKIES.get(COOKIE_NAME))
    profile = load_profile(user_id)
    attempts = profile.get("attempts", [])[:50]
    nickname = (profile.get("nickname") or "").strip() or "Гость"
    response = render(
        request,
        "trainer/history.html",
        {"attempts": attempts, "nickname": nickname},
    )
    return _with_uid_cookie(response, user_id)

