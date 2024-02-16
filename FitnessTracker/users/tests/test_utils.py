import time

from django.test import TestCase, override_settings
from django.core import mail
from users.utils import send_activation_link
from users.models import User
from django.test.client import Client
from bs4 import BeautifulSoup
from users.forms import RegistrationForm
from users.tests.test_globals import (
    REGISTRATION_FORM_FIELDS,
)


class TestUserUtilities(TestCase):
    def setUp(self):
        self.user = RegistrationForm(REGISTRATION_FORM_FIELDS).save(commit=False)
        self.user.is_active = False
        self.user.save()
        self.client = Client()

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_send_email_confirmation(self):
        # Make sure user isn't active
        self.assertFalse(self.user.is_active)

        # Get request from client and send activation link
        response = self.client.get("users/registration/")
        request = response.wsgi_request
        send_activation_link(request, self.user)

        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)

        # Get the sent email
        email = mail.outbox[0]

        # Verify email content
        self.assertEqual(email.subject, "Fitness Tracker Registration Confirmation")
        self.assertEqual(email.to, [self.user.email])

        # Retrieve the HTML version of the email
        html_content = email.alternatives[0][0]
        soup = BeautifulSoup(html_content, "html.parser")
        link_url = soup.find("a")["href"]

        # Check that link in plain text and html version match
        self.assertIn(link_url, email.body)

        # Simulate clicking activation link and check user is active
        response = self.client.get(link_url)
        self.user = User.objects.get(username=self.user.username)
        self.assertTrue(self.user.is_active)
