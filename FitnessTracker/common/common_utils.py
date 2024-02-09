import json


def save_json(data: dict, file_name: str) -> None:
    """
    Save the passed data as file_name.json.

    Args:
        data (dict): The data to be saved.
        file_name (str): The name of the JSON file.

    Returns:
        None
    """
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)


def read_json(file_name: str) -> dict:
    """
    Reads data from file_name.json and returns a dict.

    Args:
        file_name (str): The name of the JSON file.

    Returns:
        dict: The data read from the JSON file.
    """
    with open(file_name, "r") as json_file:
        data = json.loads(json_file)
        return data
