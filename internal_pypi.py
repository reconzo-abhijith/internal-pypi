"""A package for uploading files to a simple API repo."""

__version__ = "0.1.0"

import re
from pathlib import Path


def main(repo):
    get_package_names(repo)
    update_root_index_html()
    update_package_index_htmls()


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def get_package_names(repo: str) -> list[str]:
    repo_path = Path(repo)
    dirs = [item for item in repo_path.iterdir() if item.is_dir()]
    if not dirs:
        raise ValueError("No package folders found.")
    if not all(str(dirname).isascii() for dirname in dirs):
        raise ValueError("Non ascii characters found in package names.")
    return [normalize(str(dirname.stem)) for dirname in dirs]


def update_root_index_html(): ...


def update_package_index_htmls(): ...


if __name__ == "__main__":
    packages_in_repo = get_package_names("abc")
    print(packages_in_repo)
