from django.urls import reverse
from django.test import Client
from django.contrib.auth import login
from common.test_globals import USERNAME_VALID, PASSWORD_VALID


def form_without_csrf_token(page, form_data, login=False):
    client = Client(enforce_csrf_checks=True)
    client.login(username=USERNAME_VALID, password=PASSWORD_VALID) if login else None
    response = client.post(reverse(page), data=form_data)
    return response.status_code


def form_with_invalid_csrf_token(page, form_data, login=False):
    client = Client(enforce_csrf_checks=True)
    client.login(username=USERNAME_VALID, password=PASSWORD_VALID) if login else None
    response = client.post(
        reverse(page), data={**form_data, "csrfmiddlewaretoken": "invalid_token"}
    )
    return response.status_code


def form_with_valid_csrf_token(page, form_data, login=False):
    client = Client(enforce_csrf_checks=True)
    client.login(username=USERNAME_VALID, password=PASSWORD_VALID) if login else None
    response = client.get(reverse(page))
    csrf_token = response.context["csrf_token"]
    response = client.post(
        reverse(page), data={**form_data, "csrfmiddlewaretoken": csrf_token}
    )
    return response.status_code


def get_cookie_expiration_time(driver, cookie_name):
    """
    Gets the expiration time of a specific cookie.

    Args:
        driver: The Chrome WebDriver instance.
        cookie_name (str): The name of the cookie.

    Returns:
        int: The expiration time of the cookie.
    """
    # Get all cookies
    cookies = driver.get_cookies()

    # Find the specific cookie by name
    target_cookie = next(
        (cookie for cookie in cookies if cookie["name"] == cookie_name), None
    )

    # Extract and return the expiration time of the cookie
    if target_cookie:
        if "expiry" in target_cookie:
            return target_cookie["expiry"]

    return 0
