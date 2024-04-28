from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

SELECTOR_TYPE = {
    "id": By.ID,
    "name": By.NAME,
    "class": By.CLASS_NAME,
    "tag": By.TAG_NAME,
    "css": By.CSS_SELECTOR,
    "xpath": By.XPATH,
}


def select(
    driver: webdriver.Chrome, selector_type: str, selector_value: str, choice: str
) -> None:
    """
    Selects an option in a dropdown by visible text.

    Args:
        driver (webdriver.Chrome): The Chrome WebDriver instance.
        selector_type (str): The type of selector to use ('id', 'name', 'class').
        selector_value (str): The value of the selector.
        choice (str): The visible text of the option to select.

    Returns:
        None
    """
    # Find dropdown menu
    dropdown = find_element(driver, selector_type, selector_value)

    # Select choice
    Select(dropdown).select_by_visible_text(choice)


def fill_form(driver: webdriver.Chrome, form_fields: dict) -> None:
    """
    Fills a form with the provided field values.

    Args:
        driver (webdriver.Chrome): The Chrome WebDriver instance.
        form_fields (dict): Dictionary containing field names and their corresponding values.

    Returns:
        None
    """
    # Iterate over form fields
    for field_name, field_value in form_fields.items():
        # Enter values
        driver.find_element(By.NAME, field_name).send_keys(field_value)


def clear_form(driver: webdriver.Chrome, form_fields: dict) -> None:
    for field_name, field_value in form_fields.items():
        driver.find_element(By.NAME, field_name).clear()


def click(driver: webdriver.Chrome, selector_type, selector_value) -> None:
    """
    Clicks on an element identified by the given selector.

    Args:
        driver (webdriver.Chrome): The Chrome WebDriver instance.
        selector_type: The type of selector to use ('id', 'name', 'class').
        selector_value: The value of the selector.

    Returns:
        None
    """
    element = find_element(driver, selector_type, selector_value)
    element.click()


def find_element(
    driver: webdriver.Chrome | WebElement, selector_type: str, selector_value: str
) -> WebElement | None:
    """
    Finds and returns a WebElement using the provided selector.

    Args:
        driver (webdriver.Chrome): The Chrome WebDriver instance.
        selector_type (str): The type of selector to use ('id', 'name', 'class').
        selector_value (str): The value of the selector.

    Returns:
        WebElement: The found WebElement. Not found returns None.
    """
    try:
        return driver.find_element(SELECTOR_TYPE[selector_type], selector_value)
    except NoSuchElementException:
        return None


def find_elements(
    driver: webdriver.Chrome | WebElement, selector_type: str, selector_value: str
) -> list[WebElement] | None:
    """
    Finds and returns a list of WebElements using the provided selector.

    Args:
        driver (webdriver.Chrome): The Chrome WebDriver instance.
        selector_type (str): The type of selector to use ('id', 'name', 'class').
        selector_value (str): The value of the selector.

    Returns:
        list[WebElement]: The found WebElements. Not found returns None.
    """
    try:
        return driver.find_elements(SELECTOR_TYPE[selector_type], selector_value)
    except NoSuchElementException:
        return None


def elements_exist(driver: webdriver.Chrome, elements: dict) -> bool:
    """
    Checks if a set of elements exist on the page.

    Args:
        driver (webdriver.Chrome): The Chrome WebDriver instance.
        elements (dict): Dictionary containing selector types and values.

    Returns:
        bool: True if all elements exist, False otherwise.
    """
    # Iterate over items
    for selector_type, selector_values in elements.items():
        if not _elements_exist_helper(driver, selector_type, selector_values):
            return False
    return True


def _elements_exist_helper(driver: webdriver.Chrome, selector_type, selector_values):
    for value in selector_values:
        # Find next element
        elements = find_elements(driver, selector_type, value)
        # Check if any of current element exist
        if len(elements) == 0:
            return False
    return True


def login(driver: webdriver.Chrome, url: str, form_fields: dict) -> None:
    """
    Navigates chromedriver to login page and submits login form with given arguments.

    Args:
        driver (webdriver.Chrome): The Chrome WebDriver instance.
        url: The login page url.
        form_fields (dict): Dictionary containing field names and their corresponding values.

    Returns:
        webdriver.Chrome: The updated Chrome WebDriver instance.
    """
    driver.get(url)
    fill_form(driver, form_fields)
    click(driver, "name", "login")


def capture_screenshot(driver: webdriver.Chrome, file_name: str):
    """
    Capture a screenshot of the current webpage selenium driver is on and save it
    to file using file_name.

    Args:
        driver (webdriver.Chrome): The Chrome WebDriver instance.
        file_name (str): The name of the screenshot file.

    Returns:
        None
    """
    driver.save_screenshot("auctions/static/tests/" + file_name + ".png")


def validate_required_fields(driver, form_id, required_fields) -> bool:
    form = find_element(driver, "id", form_id)
    inputs = find_elements(form, "tag", "input")

    for form_input in inputs:
        if (
            form_input.get_attribute("required")
            and form_input.get_attribute("name") not in required_fields
        ):
            return False

    return True


def get_value(driver: webdriver.Chrome, selector_type: str, selector_value: str):
    try:
        element = find_element(driver, selector_type, selector_value)
        return element.get_attribute("value")
    except NoSuchElementException as e:
        print(f"No element found with {selector_type}='{selector_value}'")
        return None


def is_selected(
    driver: webdriver.Chrome, selector_type: str, selector_value: str
) -> bool:
    try:
        element = find_element(driver, selector_type, selector_value)
        return element.is_selected()
    except NoSuchElementException as e:
        print(f"No element found with {selector_type}='{selector_value}'")
        return False


def wait_until_visible(
    driver: webdriver.Chrome, selector_type: str, selector_value: str
) -> WebElement:
    wait = WebDriverWait(driver, 5)
    return wait.until(
        EC.visibility_of_element_located((SELECTOR_TYPE[selector_type], selector_value))
    )


def set_date(driver, element_id, date_value):
    driver.execute_script(
        f"document.getElementById('{element_id}').value = '{date_value}';"
    )


def drag_y(driver, selector_type, selector_value, y_value):
    element_to_drag = find_element(driver, selector_type, selector_value)
    ActionChains(driver).click_and_hold(element_to_drag).move_by_offset(
        0, y_value
    ).release().perform()
