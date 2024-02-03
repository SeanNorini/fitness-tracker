from django.test import TestCase
from django.test import LiveServerTestCase
from selenium import webdriver


# Create your tests here.
class TestUsers(LiveServerTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.browser = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    def test_login_elements(self):
        pass
