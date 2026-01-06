import tempfile
from pathlib import Path

import pytest

import internal_pypi


@pytest.fixture
def temp_folder():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def folder_with_files_only(temp_folder):
    file_1 = Path(temp_folder) / "file_1.txt"
    file_1.touch()
    file_2 = Path(temp_folder) / "file_2.txt"
    file_2.touch()
    return temp_folder


@pytest.fixture
def folder_with_invalid_folders(temp_folder):
    folder_1 = Path(temp_folder) / "α_folder"
    folder_1.mkdir(parents=True, exist_ok=True)
    folder_2 = Path(temp_folder) / "ε_folder"
    folder_2.mkdir(parents=True, exist_ok=True)
    return temp_folder


@pytest.fixture
def folder_with_valid_folders(temp_folder):
    folder_1 = Path(temp_folder) / "a_folder"
    folder_1.mkdir(parents=True, exist_ok=True)
    folder_2 = Path(temp_folder) / "e_folder"
    folder_2.mkdir(parents=True, exist_ok=True)
    return temp_folder


def test_no_dir_repo(folder_with_files_only):
    with pytest.raises(ValueError):
        internal_pypi.get_package_names(folder_with_files_only)


def test_non_ascii_name(folder_with_invalid_folders):
    with pytest.raises(ValueError):
        internal_pypi.get_package_names(folder_with_invalid_folders)


def test_valid_structure(folder_with_valid_folders):
    assert set(internal_pypi.get_package_names(folder_with_valid_folders)) == set(
        [
            "a-folder",
            "e-folder",
        ]
    )


def test_name_normalization():
    assert internal_pypi.normalize("...---...__") == "-"
    assert internal_pypi.normalize("...aba--...__") == "-aba-"
