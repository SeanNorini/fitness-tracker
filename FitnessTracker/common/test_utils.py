from django.urls import reverse
from django.test import Client


def form_without_csrf_token(page, form_data):
    client = Client(enforce_csrf_checks=True)
    response = client.post(reverse(page), data=form_data)
    return response.status_code


def form_with_invalid_csrf_token(page, form_data):
    client = Client(enforce_csrf_checks=True)
    response = client.post(
        reverse(page), data={**form_data, "csrfmiddlewaretoken": "invalid_token"}
    )
    return response.status_code


def form_with_valid_csrf_token(page, form_data):
    client = Client(enforce_csrf_checks=True)
    response = client.get(reverse(page))
    csrf_token = response.context["csrf_token"]
    response = client.post(
        reverse(page), data={**form_data, "csrfmiddlewaretoken": csrf_token}
    )
    return response.status_code
