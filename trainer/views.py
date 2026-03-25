from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import SettingsForm
from .storage import COOKIE_NAME, get_or_create_user_id, load_profile, update_profile


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

