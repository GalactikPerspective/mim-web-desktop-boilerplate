from pathlib import Path
from typing import Optional, TypedDict

from yaml import safe_load

from cli.utils import EnsurePath

CONFIG_FILE = Path(__file__).parent.parent / "build_config.yml"


class RawProjectConfig(TypedDict):
    tags_url: str
    version: str
    local_dir: str
    patches_dir: str
    # src, relative_dest, fallback
    link_files: list[str]


class ProjectConfig(TypedDict):
    name: str
    tags_url: str
    version: str
    local_dir: EnsurePath
    patches_dir: EnsurePath
    # src, relative_dest, fallback
    link_files: list[tuple[EnsurePath, str, Optional[EnsurePath]]]


def get_project_config(project_key: str) -> ProjectConfig:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError("No config file found.")
    with open(CONFIG_FILE, "r") as config_file:
        data: dict[str, RawProjectConfig] = safe_load(config_file)
    project = data.get(project_key)
    if project is None:
        raise ValueError(f"Project {project_key} not found.")

    link_files: list[tuple[EnsurePath, str, Optional[EnsurePath]]] = []
    for file_def in project["link_files"]:
        paths = file_def.split(":")
        src = EnsurePath(paths[0])
        relative_dest = paths[1]
        if len(paths) == 3:
            fallback = EnsurePath(paths[2])
        else:
            fallback = None
        link_files.append((src, relative_dest, fallback))

    return {
        "name": project_key,
        "tags_url": project["tags_url"],
        "version": project["version"],
        "local_dir": EnsurePath(project["local_dir"]),
        "patches_dir": EnsurePath(project["patches_dir"]),
        "link_files": link_files,
    }
