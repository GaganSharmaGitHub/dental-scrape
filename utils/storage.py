import os
import requests
from utils.string_utils import extension_from_url
import uuid


def upload_file_from_link(link: str):
    response = requests.get(link)
    extension = extension_from_url(link)
    file_path = f"ignore/files/{uuid.uuid4()}{extension}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path
