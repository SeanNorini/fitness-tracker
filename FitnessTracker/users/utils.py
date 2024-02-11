from django.core.exceptions import ValidationError
from users.models import User


def create_user(**user_info) -> User:
    user = User.objects.create_user(**user_info, is_staff=False)
    user.save()
    return user


def send_email_confirmation(**user_info) -> None:
    # html_body = render_to_string("users/registration-email.html", user_info)
    #
    # message = EmailMultiAlternatives(
    #     subject="Your Account is now Registered.",
    #     body="mail testing",
    #     from_email=os.environ["EMAIL_HOST_USER"],
    #     to=["snorini@gmail.com"],
    # )
    # message.attach_alternative(html_body, "text/html")
    # message.send(fail_silently=False)
    pass
