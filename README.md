MiM Web / Desktop Boilerplate
===
MiM is a fork of [Element](https://element.io/), a Matrix client.

This repository holds all the build content required to build MiM for Web and Desktop. This is done by keeping all changes in patches that are directly applied over a clone of the Element's repository.


# CLI
This repository contains a CLI tool used to build and prepare the fork. This is the tool that allows using patches with ease. To use the CLI:
- Install Python dependencies with `pip install -r cli/requirements.txt`.
  - Usage of a [Virtual Environment](https://docs.python.org/3/library/venv.html) is highly recommended.
- Run `python make.py --help` for an overview of the commands.

## `build_config.yml`
This config file contains the project configurations that the CLI will use.

A project is defined by a name (the key) and has the following properties:
- `tags_url`: The direct link to the Github's API where the project tags are. This is where the CLI will find the versions and download links for said versions.
- `version`: The current version to use for the local build. This should match the name of a tag fetched from the `tags_url`.
- `local_dir`: Path relative to the repository root where the local project will be mounted. If it doesn't exist, it will be created.
- `patches_dir` Path to the directory where the patches for the mounted project will be applied from / created. If it doesn't exist, it will be created. Patches will be saved as `[file].patch`, with the same relative path as the `local_dir` (so `<local_dir>/folder/my_file.txt` will have it's patch in `<patches_dir/folder/my_file.txt.patch`>).
- `link_files`: Array of files (or directories) that should also be mounted alongside the local copy. They should be formatted as `<relative path from the repository root>:<relative path from the local_dir>:<optional fallback>` (so, for example, `./folder/my_file.txt:my_file.txt:./defaults/my_file.txt.default` would place the file in `./folder/my_file.txt` in `<local_dir>/my_file.txt`; and if `./folder/my_file.txt` does not exist, it would first copy `./defaults/my_file.txt.default` to `./folder/my_file.txt`).


# Building the fork locally
A local project can be set up by running `python make.py init <project name>`. This will clone the version configured in the `build_config.yml`, move it to the local directory, link all files and apply all patches. From there, you can interact with it regularly (install dependencies with `yarn`, run it, build it, etc).

## Saving changes
After making changes to the local copy, you can run `python make.py generate-patches <project name>` to generate the patches for the given changes. **Note:** changes to the linked files will not be reflected on this; if your linked files are _not_ symlinks, ensure that you copy over the changes you've made.


# Building the desktop version locally
To build the desktop version, first you need to package the web version as an ASAR. There's a convenience command to do this in the CLI - `python make.py generate-asar`. This command will use the `.env` and `config.json` specified in the `element-web` project in the `build_config.yml` file, so make sure to put the correct ones there before running it. After having the `webapp.asar` file, move it into the appropriate `element-desktop` local folder, and then just build it regularly for your current OS.

## Linux
To build for Linux, we can use the convenience docker file provided by Element. Just run the following commands:
- `yarn docker:setup`.
- `yarn docker:install`.
- `yarn docker:build:native`.
- `yarn docker:build`.

### CA certs
If you're building under custom certificates, you may need to include these in the docker file; simply add the following lines to `<element-desktop local_dir>/dockerbuild/Dockerfile`, right before the first `RUN curl ...` command:

```dockerfile
COPY <cert.pem on your machine> /cert.pem
ENV NODE_EXTRA_CA_CERTS=/cert.pem

COPY <cert.crt on your machine> /usr/local/share/ca-certificates/cert.crt
RUN chmod 644 /usr/local/share/ca-certificates/cert.crt && update-ca-certificates
```

### Scripts without execution permission
While setting up the local project, some cloned scripts may not have execution permission, and they need it to build the desktop version. You may need to run `chmod +x <element-desktop local_dir>/dockerbuild/setup.sh <element-desktop local_dir>/scripts/in_docker.sh`.

## Windows
To build on Windows, you need to first ensure you have all the native dependencies requirements installed and in PATH, listed in the `docs/windows-requirements.md` file of element-desktop. Building will ensure that they're all available first.

Then, you must build the native dependencies. With CMD, first run the `call vcvarsall.bat x64` script from Visual Studio build tools, then `SET PLATFORM x64`, and finally `yarn build:native` in the element-desktop folder.
- `vcvarsall.bat`'s location will vary from installation to installation. A common path would be `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat`.
- You do not need to rebuild the native modules with every change to `webapp.asar`.

After having the native dependencies built, you can build the desktop version with `yarn build`.

## MacOS
To build on MacOS, you need to first ensure you have all the native dependencies requirements, listed here:
  - Install Homebrew by following the [official guide](https://brew.sh/).
  - Install NodeJS by following [this guide](https://nodejs.org/en/download).
  - Install Rust with homebrew by following [these steps](https://formulae.brew.sh/formula/rust#default).
  - Install Python3 by selecting the latest version on [Homebrew](https://formulae.brew.sh/formula/python@3.12).
    - Make sure you link your Python3 file with Python so that node-gyp is able to spawn it. You can do this by executing the following commands in your root pc user directory.
        ```
        cd /opt/homebrew/bin
        sudo ln -sf python3 python
        ```

Then, you must build the native dependencies by running `yarn build:native`. Finally, build the desktop version with `yarn build:universal`.
