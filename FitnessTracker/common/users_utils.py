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


def read_registration(form):
    user_info = {}

    if form.is_valid():
        user_info["username"] = form.cleaned_data["username"]
        user_info["first_name"] = (
            form.cleaned_data["first_name"]
            if form.cleaned_data["first_name"]
            else "Jane"
        )
        user_info["last_name"] = (
            form.cleaned_data["last_name"] if form.cleaned_data["last_name"] else "Doe"
        )
        user_info["password"] = form.cleaned_data["password"]
        user_info["email"] = form.cleaned_data["email"]
        user_info["gender"] = form.cleaned_data["gender"]
        user_info["height"] = (
            form.cleaned_data["height"] if form.cleaned_data["height"] else 70
        )
        user_info["weight"] = (
            form.cleaned_data["weight"] if form.cleaned_data["weight"] else 180
        )
        user_info["age"] = form.cleaned_data["age"] if form.cleaned_data["age"] else 30
    else:
        raise ValidationError("Invalid form data.")

    if user_info["password"] == form.cleaned_data["confirm_password"]:
        return user_info
    else:
        raise ValidationError("Passwords did not match.")
