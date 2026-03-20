from django.http import HttpRequest, HttpResponse


def home(_request: HttpRequest) -> HttpResponse:
    return HttpResponse("Arithmetic trainer (WIP)")

