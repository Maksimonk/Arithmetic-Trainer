from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    # Позже значения будут подставляться из сохранённого прогресса.
    context = {
        "nickname": "Гость",
        "level": 1,
        "total_attempts": 0,
        "total_correct": 0,
        "correct_streak": 0,
    }
    return render(request, "trainer/home.html", context)

