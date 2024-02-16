import os
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse


def send_activation_link(request, user) -> None:
    domain = get_current_site(request).domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_token_generator.make_token(user)

    html_body = render_to_string(
        "users/registration_email.html",
        {
            "name": user.first_name,
            "email": user.email,
            "domain": domain,
            "uid": uid,
            "token": token,
        },
    )

    activate_url = reverse("activate", args=[uid, token])
    message = EmailMultiAlternatives(
        subject="Fitness Tracker Registration Confirmation",
        body=f"""Dear {user.username},

                 Thank you for registering with WTCC Fitness Tracker! To complete your registration, 
                 please visit the following URL in your web browser and follow the instructions:
                 http://{ domain }{ activate_url }
                 
                 If you did not register on our fitness tracker, you can ignore this email.
                 
                 Thank you,
                 WTCC Fitness Tracker Support Team""",
        from_email=os.environ["EMAIL_HOST_USER"],
        to=[user.email],
    )

    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)


def send_reset_link(request, user) -> None:
    domain = get_current_site(request).domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_token_generator.make_token(user)

    html_body = render_to_string(
        "users/reset_password_email_notification.html",
        {
            "name": user.username,
            "email": user.email,
            "domain": domain,
            "uid": uid,
            "token": token,
        },
    )

    reset_url = reverse("reset_password_confirm_token", args=[uid, token])
    message = EmailMultiAlternatives(
        subject="Password Reset Request",
        body=f"""Dear {user.username},
                
                You are receiving this email because a password reset request was made for your account.
                If you did not request a password reset, please ignore this email. Your password will remain unchanged.
                To reset your password, copy and paste the following URL into your browser:
                http://{ domain }{ reset_url }
                If you have any questions or need further assistance, please contact our support team.

                Thank you,
                WTCC Fitness Tracker Team""",
        from_email=os.environ["EMAIL_HOST_USER"],
        to=[user.email],
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
