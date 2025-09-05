import os
import shutil
import subprocess
from pathlib import Path
from typing import Literal
from uuid import uuid4

import click

from cli.config import get_project_config
from cli.github import get_project_folder
from cli.patcher import apply_patch_file, generate_patch, is_file_equal
from cli.utils import (
    CACHE_DIR,
    PROJECT_DIR,
    error,
    is_windows,
    log,
    read_lines,
    success,
    warning,
    write_lines,
)


@click.group
def cli_instance() -> None:
    pass


@cli_instance.command
@click.option(
    "--link-mode",
    type=click.Choice(["symlink", "copy"]),
    default="symlink",
    help="How to handle overrides MiM folder",
)
@click.option("-s", "--skip-bad-patches", is_flag=True, help="If a patch fails, do not abort.")
@click.option("-y", "--yes", is_flag=True, help="Yes to all prompts.")
@click.argument("project")
def init(project: str, link_mode: Literal["symlink", "copy"], yes: bool, skip_bad_patches: bool) -> None:
    """Initialize the local copy of the specified project."""
    try:
        project_config = get_project_config(project)
    except Exception as e:
        error(f"Failed to retrieve project '{project}' from config file.")
        raise click.Abort() from e

    log(f"Initializing repository for {project_config['name']} version '{project_config['version']}'.")

    # Load the project version into cache
    try:
        project_dir = get_project_folder(project_config)
    except Exception as e:
        error(f"Failed to retrieve {project} version '{project_config['version']}'.")
        raise click.Abort() from e

    local_dir = project_config["local_dir"]

    # Copy it
    if local_dir.exists():
        warning(f"Local folder found at '{local_dir.as_posix()}'.")
        if not yes:
            click.confirm(
                f"This will delete all it's contents. {click.style('Are you sure you want to proceed?', bold=True)}",
                abort=True,
            )
        shutil.rmtree(local_dir.resolve())
    shutil.copytree(project_dir, local_dir)
    success(f"Copied version {project_config['name']} '{project_config['version']}' to '{local_dir.as_posix()}'.")

    # Check for fallbacks on link files
    for src, _, fallback in project_config["link_files"]:
        if not src.exists():
            if fallback is None:
                error(f"Linked file '{src.as_posix()}' not found with no fallback. Using empty file.")
                src.touch()
            else:
                warning(f"Linked file '{src.as_posix()}' not found. Using fallback '{fallback.as_posix()}'.")
                if fallback.is_dir():
                    shutil.copytree(fallback, src)
                else:
                    shutil.copy(fallback, src)

    # Attempt to link / copy files
    def copy_linked_files_aux() -> None:
        for src, relative_dest, _ in project_config["link_files"]:
            dest = local_dir / relative_dest
            if src.is_dir():
                shutil.copytree(src, dest)
            else:
                shutil.copy(src, dest)
            log(f"Linked {'folder' if src.is_dir() else 'file'} copied from {src.as_posix()} to {dest.as_posix()}.")
        success("Linked files copied successfully.")

    match link_mode:
        case "symlink":
            try:
                for src, relative_dest, _ in project_config["link_files"]:
                    dest = local_dir / relative_dest
                    os.symlink(src, dest, src.is_dir())
                    log(f"Symlink created from {src.as_posix()} to {dest.as_posix()}.")
                success("Linked files symlinked successfully.")
            except OSError:
                if yes or click.confirm(
                    click.style("Failed to create symlinks for the linked files - copy instead?", fg="yellow")
                ):
                    copy_linked_files_aux()
                else:
                    warning("Linked files not copied nor linked. Skipping.")
        case "copy":
            copy_linked_files_aux()

    # Apply the patches
    if not project_config["patches_dir"].exists():
        warning("Patches folder not found. Skipping.")
    else:
        count = 0
        skipped = 0
        for file_path in project_config["patches_dir"].rglob("*"):
            if file_path.is_dir():
                continue
            # Find the corresponding project file
            relative_path = file_path.relative_to(project_config["patches_dir"])
            if file_path.suffix != ".patch":
                warning(f"File '{file_path.as_posix()}' is not a patch. Skipping.")
                continue
            unsuffixed = relative_path.with_suffix("")  # remove .patch
            patch_file = project_config["patches_dir"] / unsuffixed.with_suffix(unsuffixed.suffix + ".patch")
            local_file = project_config["local_dir"] / unsuffixed

            if not local_file.exists():
                error(f"File '{unsuffixed.as_posix()}' missing from local project while patch exists. Skipping.")
                continue

            try:
                read_lines(file_path)
                try:
                    apply_patch_file(patch_file, local_file)
                except Exception:
                    if skip_bad_patches:
                        skipped += 1
                        warning(f"Failed to apply patch to {unsuffixed.as_posix()} - keeping original file.")
                        continue
                    raise
            except UnicodeDecodeError:
                # It's binary; copy it instead
                shutil.copy(patch_file, local_file)

            count += 1

            log(f"Applied patch to '{unsuffixed.as_posix()}'.")
        if skipped == 0:
            success(f"Applied {count} patches successfully.")
        else:
            warning(f"Applied {count} patches successfully ({skipped} skipped).")

    success(f"Project {project_config['name']} version '{project_config['version']}' successfully initialized.")


@cli_instance.command
@click.argument("project")
def generate_patches(project: str) -> None:
    """Generate patches from the local copy of the specified project."""
    try:
        project_config = get_project_config(project)
    except Exception as e:
        error(f"Failed to retrieve project '{project}' from config file.")
        raise click.Abort() from e
    log(f"Generating patches for {project_config['name']} version '{project_config['version']}' from local copy.")

    # Load the project version into cache
    try:
        project_dir = get_project_folder(project_config)
    except Exception as e:
        error(f"Failed to retrieve {project} version '{project_config['version']}'.")
        raise click.Abort() from e

    # Get the local folder
    local_dir = project_config["local_dir"]
    if not local_dir.exists():
        error("Local directory not found. Aborting.")
        raise click.Abort()

    # Create a temporary dir in cache to generate the patches there first
    temporary_dir = CACHE_DIR / str(uuid4())
    temporary_dir.ensure()

    # Iterate over the original files to compare with the local files
    for file_path in project_dir.rglob("*"):
        if file_path.is_dir():
            continue
        relative_path = file_path.relative_to(project_dir)
        element_file = project_dir / relative_path
        local_file = local_dir / relative_path

        if not local_file.exists():
            # Local file was deleted?
            error(f"File {relative_path} not found in the local project.")
            continue
        if is_file_equal(element_file, local_file):
            # Nothing to patch
            continue

        patch_file = (temporary_dir / relative_path).with_suffix(relative_path.suffix + ".patch")
        patch_file.parent.ensure()

        try:
            patch = generate_patch(element_file, local_file)
            if "".join(patch).strip() == "":
                # Files are considered different but no patch?
                continue
            write_lines(patch_file, patch)
        except UnicodeDecodeError:
            # File is binary - simply copy it
            shutil.copy(local_file, patch_file)

    patches_dir = project_config["patches_dir"]
    patches_dir.ensure()

    # Update the user on changes - creates / updated
    for file_path in temporary_dir.rglob("*"):
        if file_path.is_dir():
            continue
        relative_path = file_path.relative_to(temporary_dir)
        patch_path = patches_dir / relative_path

        is_binary = False
        try:
            read_lines(file_path)
        except UnicodeDecodeError:
            is_binary = True

        if patch_path.exists() and not is_file_equal(file_path, patch_path):
            warning(
                f"Patch for '{relative_path.with_suffix('').as_posix()}' {'(binary) ' if is_binary else ''}was updated."
            )
        elif not patch_path.exists():
            success(
                f"Patch for '{relative_path.with_suffix('').as_posix()}' {'(binary) ' if is_binary else ''}was created."
            )

    # Update the user on changes - deletes
    for file_path in patches_dir.rglob("*"):
        if file_path.is_dir():
            continue
        relative_path = file_path.relative_to(patches_dir)

        is_binary = False
        try:
            read_lines(file_path)
        except UnicodeDecodeError:
            is_binary = True

        if not (temporary_dir / relative_path).exists():
            warning(
                f"Patch for '{relative_path.with_suffix('').as_posix()}' {'(binary) ' if is_binary else ''}was deleted."
            )

    # Copy the patches from the temporary dir to the patches dir
    shutil.rmtree(patches_dir)
    shutil.copytree(temporary_dir, patches_dir)
    shutil.rmtree(temporary_dir)

    success("Finished generating patches.")


@cli_instance.command
@click.option("-y", "--yes", is_flag=True, help="Yes to all prompts.")
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True, path_type=Path),
    default=PROJECT_DIR / "webapp.asar",
)
@click.argument("element-project", default="element-web")
def generate_asar(element_project: str, output: Path, yes: bool) -> None:
    """Generate an ASAR from the Element-Web fork base."""

    try:
        project_config = get_project_config(element_project)
    except Exception as e:
        error(f"Failed to retrieve project '{element_project}' from config file.")
        raise click.Abort() from e

    if not yes and "element-hq/element-web" not in project_config["tags_url"]:
        click.confirm(
            "This project does not look like it points to a version of element-web. Are you sure you selected the right project?",
            abort=True,
        )

    log(f"Generating ASAR file for {project_config['name']} version '{project_config['version']}'.")

    # Load the project version into cache
    try:
        project_dir = get_project_folder(project_config)
    except Exception as e:
        error(f"Failed to retrieve {element_project} version '{project_config['version']}'.")
        raise click.Abort() from e

    # Copy it to a temporary folder
    temporary_dir = CACHE_DIR / str(uuid4())
    shutil.copytree(project_dir, temporary_dir)

    # Check for fallbacks on link files
    for src, _, fallback in project_config["link_files"]:
        if not src.exists():
            if fallback is None:
                error(f"Linked file '{src.as_posix()}' not found with no fallback. Using empty file.")
                src.touch()
            else:
                warning(f"Linked file '{src.as_posix()}' not found. Using fallback '{fallback.as_posix()}'.")
                if fallback.is_dir():
                    shutil.copytree(fallback, src)
                else:
                    shutil.copy(fallback, src)

    # Copy the link files
    for src, relative_dest, _ in project_config["link_files"]:
        dest = temporary_dir / relative_dest
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy(src, dest)
    success("Successfully copied link files.")

    # Apply the patches
    if not project_config["patches_dir"].exists():
        warning("Patches folder not found. Skipping.")
    else:
        count = 0
        for file_path in project_config["patches_dir"].rglob("*"):
            if file_path.is_dir():
                continue
            # Find the corresponding project file
            relative_path = file_path.relative_to(project_config["patches_dir"])
            if file_path.suffix != ".patch":
                warning(f"File '{file_path.as_posix()}' is not a patch. Skipping.")
                continue
            unsuffixed = relative_path.with_suffix("")  # remove .patch
            patch_file = project_config["patches_dir"] / unsuffixed.with_suffix(unsuffixed.suffix + ".patch")
            local_file = temporary_dir / unsuffixed

            if not local_file.exists():
                error(f"File '{unsuffixed.as_posix()}' missing from local project while patch exists. Skipping.")
                continue

            try:
                read_lines(file_path)
                apply_patch_file(patch_file, local_file)
            except UnicodeDecodeError:
                # It's binary; copy it instead
                shutil.copy(patch_file, local_file)

            count += 1

        success(f"Applied {count} patches successfully.")

    # Install dependencies and build the project
    log("Installing dependencies with yarn...")
    subprocess.run(["yarn"], check=True, stdout=subprocess.DEVNULL, cwd=temporary_dir, shell=is_windows)
    success("Successfully installed dependencies.")
    log("Building webapp folder...")
    subprocess.run(["yarn", "build"], check=True, stdout=subprocess.DEVNULL, cwd=temporary_dir, shell=is_windows)
    success("Successfully built webapp folder.")

    # Also apply the replace script on the generated folder
    log("Applying replace_vars.sh script...")
    env_file = temporary_dir / ".env"
    target = temporary_dir / "webapp" / "index.html"

    subprocess.run(
        ["bash", "./replace_vars.sh", "-e", env_file.as_posix(), target.as_posix()],
        check=True,
        stdout=subprocess.DEVNULL,
        cwd=(PROJECT_DIR / "projects" / "element-web" / "scripts"),
        shell=is_windows,
    )
    success("Successfully applied")

    log("Packaging ASAR...")
    filename = "webapp.asar"
    subprocess.run(
        ["npx", "--yes", "@electron/asar", "pack", "webapp", filename],
        check=True,
        stdout=subprocess.DEVNULL,
        cwd=temporary_dir,
        shell=is_windows,
    )
    success("Successfully packaged with ASAR.")
    log(f"Copying to '{output.relative_to(PROJECT_DIR).as_posix()}'...")
    shutil.copy(temporary_dir / filename, output)
    success("Finished generating ASAR!")
    shutil.rmtree(temporary_dir)  # Delete the temporary folder
