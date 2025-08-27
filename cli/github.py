import requests
import shutil
import zipfile
from pathlib import Path
from typing import TypedDict

from cli.config import ProjectConfig
from cli.utils import CACHE_DIR, error, success, warning


class CommitData(TypedDict):
    sha: str
    url: str


class TagData(TypedDict):
    """Formatted data as given by the Github API."""

    name: str
    zipball_url: str
    tarball_url: str
    commit: CommitData
    node_id: str


def download_and_extract_repo(project_data: ProjectConfig) -> None:
    name = project_data["name"]
    version = project_data["version"]

    # Get the version from the repository tags
    tags_res = requests.get(project_data["tags_url"])
    tags_data: list[TagData] = tags_res.json()

    # Check if we need to download it
    zip_path = CACHE_DIR / name / f"{version}.zip"
    if not zip_path.exists():
        warning(f"Downloading {name} version '{version}'...")
        version_data = next((tag for tag in tags_data if tag["name"] == version), None)
        if not version_data:
            error(f"Version '{version}' not found in the {name} repository!")
            raise ValueError(f"Version {version} not found in the repository.")

        # Download it
        download = requests.get(version_data["zipball_url"], stream=True)
        if not download.ok:
            error(f"Download failed with status code {download.status_code}.")
            download.raise_for_status()
        zip_path.parent.ensure()
        with open(zip_path, "+wb") as out_file:
            shutil.copyfileobj(download.raw, out_file)

    # Extract it
    destination = CACHE_DIR / name / version
    destination.ensure()
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        files = zip_file.infolist()
        for file_path in files[1:]:
            if file_path.is_dir():
                continue
            file_path.filename = "/".join(file_path.filename.split("/")[1:])
            zip_file.extract(file_path, destination)


def get_project_folder(project_data: ProjectConfig) -> Path:
    name = project_data["name"]
    version = project_data["version"]

    folder_path = CACHE_DIR / name / version
    if folder_path.exists():
        success(f"Version '{version}' for {name} found in cache.")
    else:
        warning(f"Version '{version}' for {name} not found in cache.")
        download_and_extract_repo(project_data)
    return folder_path
