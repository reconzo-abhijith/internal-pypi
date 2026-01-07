import tempfile
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

import internal_pypi


@pytest.fixture
def temp_file():
    with tempfile.NamedTemporaryFile() as tmpfile:
        yield tmpfile.name


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
    folder_2 = Path(temp_folder) / ".e_folder"
    folder_2.mkdir(parents=True, exist_ok=True)
    return Path(temp_folder)


@pytest.fixture
def folder_with_tar_gz_files(temp_folder):
    f1 = Path(temp_folder) / "f1.tar.gz"
    f1.touch()
    f2 = Path(temp_folder) / "f2.tar.gz"
    f2.touch()
    return temp_folder


@pytest.fixture
def folder_with_whl_files(temp_folder):
    f1 = Path(temp_folder) / "reconzo_utilities-1.0.8-none-any.whl"
    f1.touch()
    f2 = Path(temp_folder) / "f2.tar.gz"
    f2.touch()
    return temp_folder


def test_valid_structure(folder_with_valid_folders):
    assert set(
        internal_pypi.normalize_package_folder_names(folder_with_valid_folders)
    ) == set(
        [
            "a-folder",
            "-e-folder",
        ]
    )
    assert (Path(folder_with_valid_folders) / "a-folder").exists()
    assert not (Path(folder_with_valid_folders) / ".e-folder").exists()
    assert (Path(folder_with_valid_folders) / "-e-folder").exists()


def test_name_normalization():
    assert internal_pypi.normalize("...---...__") == "-"
    assert internal_pypi.normalize("...aba--...__") == "-aba-"


def test_name_validity():
    assert not internal_pypi.is_valid_name("A name with spaces")
    assert internal_pypi.is_valid_name("A_Name_w1th0ut-spaces.whl")


def test_file_backup(temp_folder, temp_file):
    source_file = Path(temp_folder) / temp_file
    backed_up_file = internal_pypi.backup_file(temp_folder, filename=temp_file)
    assert backed_up_file.exists() == source_file.exists()


def test_file_backup_nonexistent():
    # This basically ensures that if the file is absent, then the backup is too.
    ne_folder = r"/does/not"
    ne_file = "exist.txt"
    source_file = Path(ne_folder) / ne_file
    backed_up_file = internal_pypi.backup_file(ne_folder, filename=ne_file)
    assert backed_up_file.exists() == source_file.exists()


def test_root_index_html(folder_with_valid_folders):
    root_index_html = internal_pypi.make_root_index_html(folder_with_valid_folders)
    with open(root_index_html) as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, "html.parser")
    anchor_tags = soup.find_all("a")
    anchor_texts = [tag.get_text() for tag in anchor_tags]
    assert set(anchor_texts) == set(
        internal_pypi.normalize_package_folder_names(folder_with_valid_folders)
    )


def test_getting_tar_gz_files(folder_with_tar_gz_files):
    tar_gz_files = internal_pypi.get_tar_gz_files(Path(folder_with_tar_gz_files))
    assert set((f.stem + f.suffix) for f in tar_gz_files) == set(
        ["f1.tar.gz", "f2.tar.gz"]
    )


def test_getting_whl_files(folder_with_whl_files):
    whl_files = internal_pypi.get_whl_files(Path(folder_with_whl_files))
    assert set((f.stem + f.suffix) for f in whl_files) == set(
        ["reconzo_utilities-1.0.8-none-any.whl"]
    )
