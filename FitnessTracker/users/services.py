from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import six
import os


def change_user_password(
    user, current_password, new_password, confirm_password, **kwargs
):
    if new_password != confirm_password:
        return {"confirm_password": ["Passwords don't match"]}

    if not user.check_password(current_password):
        return {"current_password": ["Incorrect password"]}

    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return {"new_password": e.messages}

    user.set_password(new_password)
    user.save()
    return {}


class EmailService:

    def __init__(self, request, user):
        self.request = request
        self.user = user
        self.domain = self.get_domain()
        self.uid = self.get_uid()
        self.token = self.get_token()

    def get_domain(self):
        return get_current_site(self.request).domain

    def get_uid(self):
        return urlsafe_base64_encode(force_bytes(self.user.pk))

    def get_token(self):
        return account_token_generator.make_token(self.user)

    def send_activation_link(self):
        html_body = self.create_html_body("users/registration_email.html")
        activate_url = reverse("activate", args=[self.uid, self.token])
        self.send_email(
            subject="Fitness Tracker Registration Confirmation",
            body_template="""Dear {username},

                             Thank you for registering with WTCC Fitness Tracker! To complete your registration, 
                             please visit the following URL in your web browser and follow the instructions:
                             http://{domain}{activate_url}

                             If you did not register on our fitness tracker, you can ignore this email.

                             Thank you,
                             WTCC Fitness Tracker Support Team""",
            html_body=html_body,
            url=activate_url,
        )

    def send_reset_link(self):
        html_body = self.create_html_body(
            "users/reset_password_email_notification.html"
        )
        reset_url = reverse("reset_password_confirm_token", args=[self.uid, self.token])
        self.send_email(
            subject="Password Reset Request",
            body_template="""Dear {username},

                            You are receiving this email because a password reset request was made for your account.
                            If you did not request a password reset, please ignore this email. Your password will remain unchanged.
                            To reset your password, copy and paste the following URL into your browser:
                            http://{domain}{reset_url}
                            If you have any questions or need further assistance, please contact our support team.

                            Thank you,
                            WTCC Fitness Tracker Team""",
            html_body=html_body,
            url=reset_url,
        )

    def create_html_body(self, template_name):
        return render_to_string(
            template_name,
            {
                "name": self.user.username,
                "domain": self.domain,
                "uid": self.uid,
                "token": self.token,
            },
        )

    def send_email(self, subject, body_template, html_body, url):
        message_body = body_template.format(
            username=self.user.username,
            domain=self.domain,
            activate_url=url,
            reset_url=url,
        )

        message = EmailMultiAlternatives(
            subject=subject,
            body=message_body,
            from_email=os.environ["EMAIL_HOST_USER"],
            to=[self.user.email],
        )
        message.attach_alternative(html_body, "text/html")
        message.send(fail_silently=False)


class AccountTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk)
            + six.text_type(timestamp)
            + six.text_type(user.is_active)
        )


account_token_generator = AccountTokenGenerator()
