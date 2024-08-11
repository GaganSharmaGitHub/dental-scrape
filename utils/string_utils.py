import os
import re
from urllib.parse import urlparse


def get_last_part_of_url(url: str):
    parsed_url = urlparse(url)
    path = parsed_url.path
    last_part = path.strip("/").split("/")[-1]
    return last_part


def extract_float(s: str):
    pattern = r"-?\d+\.?\d*"
    match = re.search(pattern, s)

    if match:
        return float(match.group())
    else:
        return None


def extension_from_url(url: str):
    parsed_url = urlparse(url)
    path = parsed_url.path
    file_extension = os.path.splitext(path)[1]
    return file_extension
