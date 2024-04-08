USERNAME_VALID = "new_user"
USERNAME_INVALID = "invalid"
PASSWORD_VALID = "new_user_password"
PASSWORD_INVALID = "invalid_pass"
EMAIL_VALID = "new_user@gmail.com"
EMAIL_INVALID = "invalid@@gmail.com@"

MIN_LENGTH_NAME = 2
MIN_LENGTH_PASSWORD = 8
MAX_LENGTH_NAME_OR_PASSWORD = 100
MAX_LENGTH_USERNAME_OR_EMAIL = 254

LOGIN_USER_FORM_FIELDS = {"username": "new_user", "password": "new_user_password"}

CREATE_USER = {
    "username": "new_user",
    "password": "new_user_password",
    "first_name": "first",
    "last_name": "last",
    "email": "new_user@gmail.com",
    "gender": "M",
    "weight": 150,
    "height": 75,
    "age": 28,
}

REGISTRATION_FORM_FIELDS = {
    "username": "new_user2",
    "password": "new_user_password",
    "confirm_password": "new_user_password",
    "first_name": "first",
    "last_name": "last",
    "email": "smnorini@gmail.com",
    "gender": "M",
    "weight": "150",
    "height": "75",
    "age": "28",
}


CHANGE_PASSWORD_FORM_FIELDS = {
    "current_password": "new_user_password",
    "new_password": "test_pass123",
    "confirm_password": "test_pass123",
}
