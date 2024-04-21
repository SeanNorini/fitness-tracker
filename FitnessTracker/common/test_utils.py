from django.contrib.auth import login
from common.test_globals import USERNAME_VALID, PASSWORD_VALID, CREATE_USER
from django.test import Client
from django.urls import reverse
from bs4 import BeautifulSoup
import abc
from users.models import User, UserSettings
from unittest import skipIf
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver


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
    if login:
        client.login(username=USERNAME_VALID, password=PASSWORD_VALID)
    client.get(reverse("login"))

    csrf_token = (
        client.cookies.get("csrftoken").value
        if client.cookies.get("csrftoken")
        else None
    )

    response = client.post(
        reverse(page), data={**form_data, "csrfmiddlewaretoken": csrf_token}
    )
    return response.status_code


def elements_exist(soup, elements):
    """
    Check if all elements exist in the soup.
    Elements should be a dictionary with keys as attributes and values as lists of values for those attributes.
    Example: {"id": ["btn-login", "header"], "name": ["username", "password"]}
    """
    for attr, values in elements.items():
        for value in values:
            if not soup.find(attrs={attr: value}):
                return False
    return True


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


class ViewSharedTests(metaclass=abc.ABCMeta):
    url = None
    title = None
    elements = []
    regular_template = None
    fetch_template = None

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", password="testpassword", email="test@test.com"
        )
        cls.user_settings = UserSettings.objects.create(user=cls.user)

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)

    def test_elements_and_title(self):
        """Verifies the existence of expected elements and title"""
        soup = BeautifulSoup(self.response.content, "html.parser")
        title_tag = soup.find("title")
        self.assertIsNotNone(title_tag, "Title tag not found")
        self.assertEqual(title_tag.text, self.title)

        for element in self.elements:
            self.assertTrue(
                soup.find(attrs=element), f"Element {element} not found on page."
            )

    def test_view_regular_request(self):
        """Ensures the regular request uses the correct template and responds with status 200"""
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, self.regular_template)

    @skipIf(
        lambda cls: cls.regular_template == cls.fetch_template,
        "Skipping fetch template test as it is the same as regular template",
    )
    def test_view_fetch_template(self):
        """Tests AJAX fetch template if different from regular"""
        response = self.client.get(
            self.url, **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.fetch_template)

    def test_login_required(self):
        """Tests login is required to view page"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/user/login/?next={self.url}")


class SeleniumTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        self.user = User.objects.create_user(**CREATE_USER)
