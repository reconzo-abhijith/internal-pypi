"""A package for uploading files to a simple API repo."""

__version__ = "0.1.0"

import hashlib
import re
import shutil
import string
import textwrap
from pathlib import Path


def main(repo):
    normalize_package_folder_names(repo)
    make_root_index_html(repo)


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def is_valid_name(name: str) -> bool:
    """From the spec: only valid characters in a name are the
    ASCII alphabet, ASCII numbers, ., -, and _."""
    valid_chars = set(string.ascii_letters + string.digits + ".-_")
    name_chars = set(name)
    _intersection = name_chars & valid_chars
    return _intersection == name_chars


def get_package_folders(repopath: Path) -> list[Path]:
    """Return folder paths that are valid package names."""
    return [
        item
        for item in repopath.iterdir()
        if item.is_dir() and is_valid_name(item.stem)
    ]


def normalize_package_folder_names(repopath: Path) -> list[str]:
    """Rename valid folder names as per the spec."""
    package_folders = get_package_folders(repopath)
    normalized_folder_names = []
    for folder in package_folders:
        _normalized_path = folder.parent / normalize(folder.stem)
        folder.rename(_normalized_path)
        normalized_folder_names.append(_normalized_path)
    return [item.stem for item in normalized_folder_names]


def backup_file(reponame: str, filename: str = "index.html") -> Path:
    filepath = Path(reponame) / filename
    source_filename = str(filepath)
    backup_filename = source_filename + ".bak"
    if filepath.exists():
        shutil.copyfile(source_filename, backup_filename, follow_symlinks=False)
    return Path(backup_filename)


def make_anchor_tag(fpath: Path, add_hash: str | None = None) -> str:
    """Generate a HTML anchor tag for a file or folder."""
    _four_spaces = " " * 4
    _text_val = fpath.stem + fpath.suffix
    if add_hash is None:
        return f"{_four_spaces}<a href=/{_text_val}/>{_text_val}</a>"
    elif add_hash == "sha256":
        filehash = compute_sha256(fpath)
        hash_suffix = f"#sha256={filehash}"
        return f"{_four_spaces}<a href=./{_text_val}{hash_suffix}>{_text_val}</a>"
    else:
        raise NotImplementedError("Hashing is only supported with sha256")


def compute_sha256(file_path):
    """
    Computes the SHA-256 hash of a file.

    Parameters:
    file_path (str): The path to the file.

    Returns:
    str: The SHA-256 hash of the file as a hexadecimal string.
    """
    sha256_hash = hashlib.sha256()

    # Open the file in binary mode
    with open(file_path, "rb") as file:
        # Read the file in chunks to avoid memory issues
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)

    # Return the hexadecimal digest of the hash
    return sha256_hash.hexdigest()


def make_root_index_html(repopath: Path) -> Path:
    fixed_html = textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta name="pypi:repository-version" content={__version__}>
            <title>Simple index</title>
        </head>
        <body>
        """)
    _normalized_names = normalize_package_folder_names(repopath)
    package_names = get_package_folders(repopath)
    package_anchor_tags = map(make_anchor_tag, package_names)
    _html = fixed_html + "\n".join(package_anchor_tags) + "\n</body>\n</html>"
    index_html_filepath = Path(repopath) / "index.html"
    with open(index_html_filepath, "w") as f:
        f.write(_html)
    return index_html_filepath


def get_tar_gz_files(package_path: Path) -> list[Path]:
    return [
        version_file
        for version_file in package_path.iterdir()
        if (
            version_file.is_file()
            and ("".join(version_file.suffixes[-2:]) == ".tar.gz")
        )
    ]


def get_whl_files(package_path: Path) -> list[Path]:
    return [
        version_file
        for version_file in package_path.iterdir()
        if (version_file.is_file() and version_file.suffix == ".whl")
    ]


def make_package_index_html(package_path: Path) -> Path:
    fixed_html = textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta name="pypi:repository-version" content={__version__}>
            <title>Simple index</title>
        </head>
        <body>
        """)
    tar_gz_files = get_tar_gz_files(package_path)
    whl_files = get_whl_files(package_path)
    versions = tar_gz_files + whl_files
    version_anchor_tags = map(lambda x: make_anchor_tag(x, add_hash="sha256"), versions)
    _html = fixed_html + "\n".join(version_anchor_tags) + "\n</body>\n</html>"
    index_html_filepath = package_path / "index.html"
    with open(index_html_filepath, "w") as f:
        f.write(_html)
    return index_html_filepath


if __name__ == "__main__":
    repopath = Path("prod_repo/")
    normalize_package_folder_names(repopath)
    packages_in_repo = get_package_folders(repopath)
    make_root_index_html(repopath)
    for package in packages_in_repo:
        make_package_index_html(package)
