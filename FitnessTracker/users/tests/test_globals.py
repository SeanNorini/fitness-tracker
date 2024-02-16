USERNAME_VALID = "testuser"
USERNAME_INVALID = "invalid"
PASSWORD_VALID = "testpassword"
PASSWORD_INVALID = "invalid_pass"
EMAIL_VALID = "test@gmail.com"
EMAIL_INVALID = "invalid@@gmail.com@"

LOGIN_USER_FORM_FIELDS = {"username": "testuser", "password": "testpassword"}

REGISTRATION_FORM_FIELDS = {
    "username": "new_user",
    "password": "new_user_password",
    "confirm_password": "new_user_password",
    "first_name": "first",
    "last_name": "last",
    "email": "snorini@gmail.com",
    "gender": "M",
    "weight": "150",
    "height": "75",
    "age": "28",
}

CHANGE_PASSWORD_FORM_FIELDS = {
    "current_password": "testpassword",
    "new_password": "test_pass123",
    "confirm_password": "test_pass123",
}
