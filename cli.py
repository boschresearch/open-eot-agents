# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0
import os
import sys
from pathlib import Path
from subprocess import Popen, CalledProcessError, PIPE, STDOUT
from typing import Optional, List, Any

MIN_PYTHON_VERSION = [3, 8]
AGENT_FOLDER_SUFFIX = "_agent"
AEA_PROJECT_SUFFIX = "_aea_project"
AEA_COMPONENTS_DIRECTORY = "aea_components"
PIPFILE_TEMPLATE = """
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
aea = {extras = ["all"], version = "*"}

[dev-packages]

[requires]
python_version = "3.8"
"""


def check_python_version():
    for i, v in enumerate(MIN_PYTHON_VERSION):
        if  sys.version_info[i]< v:
            print(f"At least python {'.'.join(str(p) for p in MIN_PYTHON_VERSION)} is required.")
            sys.exit(1)


def get_script_folder() -> Optional[Path]:
    script_directory = Path(__file__).resolve().parent
    local_registry_name = "packages"
    packages_directory = script_directory / local_registry_name
    if not packages_directory.is_dir() and not packages_directory.is_symlink():
        print(f"The folder {script_directory} does not contain the '{local_registry_name}' directory.")
        sys.exit(1)
    # TODO further sanity checks
    return script_directory


def create_directories_for_module(project_dir: Path, name: str) -> Path:
    component_project_dir = project_dir / AEA_COMPONENTS_DIRECTORY / f"{name}{AEA_PROJECT_SUFFIX}"
    component_project_dir.mkdir(parents=True, exist_ok=True)
    return component_project_dir


# TODO evaluate if https://python-poetry.org/ adds value over pipenv
def setup_pipenv(component_project_dir: Path):
    # TODO check, that pipenv is installed?

    pipfile = component_project_dir / "Pipfile"
    piplockfile = component_project_dir / "Pipfile.lock"
    # preferring the Pipfile.lock and not updating it with the Pipfile
    if piplockfile.exists():
        if piplockfile.is_file:
            print(f"running pipenv sync at {component_project_dir}")
            run_command_in_subprocess(["pipenv", "sync"], component_project_dir)
        else:
            raise FileNotFoundError(f"{piplockfile} is not a file")
        return

    if not pipfile.exists():
        print(f"creating {pipfile}")
        with open(pipfile, 'w') as pipfile_content:
            pipfile_content.write(PIPFILE_TEMPLATE)
    if piplockfile.is_file:
        print(f"running pipenv update at {component_project_dir}")
        run_command_in_subprocess(["pipenv", "update"], component_project_dir)
    else:
        raise FileNotFoundError(f"{pipfile} is not a file")


def kill_pip_process_on_exit(opened_subprocess: Popen):
    # TODO kill spawned process
    pass


def run_command_in_subprocess(command_line, component_project_dir):
    print(f"=== begin output: {command_line}")
    with Popen(args=command_line,
               stdin=None,
               stdout=None,
               stderr=None,
               text=True,
               cwd=component_project_dir,
               preexec_fn=os.setsid
               ) as pipenv_process:
        kill_pip_process_on_exit(pipenv_process)
        try:
            stdout, stderr = pipenv_process.communicate()
        except:
            pipenv_process.kill()
        if pipenv_process.returncode != 0:
            raise CalledProcessError(pipenv_process.returncode, pipenv_process.args,
                                     output=stdout, stderr=stderr)
    print(f"===   end output: {command_line}")


# i chose to use a subprocess and the provided cli instead of importing the aea,
# because the cli is documented and i expect it to stay more stable than the python code used by the cli
def create_aea_component_agent(component_project_dir: Path, component_name: str):
    agent_project_name = f"{component_name}{AGENT_FOLDER_SUFFIX}"
    # TODO check if aea is installed, if not suggest running with pipenv (when it was not enabled)
    command_line = ["pipenv", "run", "aea", "create", agent_project_name]
    agent_project_dir = component_project_dir / agent_project_name
    if agent_project_dir.exists():
        print(f"There is already an agent named '{agent_project_name}' at {component_project_dir}")
        sys.exit(1)
    run_command_in_subprocess(command_line, component_project_dir)
    return agent_project_dir


def scaffold_module(name: str):
    project_dir = get_script_folder()
    if project_dir is not None:
        component_project_dir = create_directories_for_module(project_dir, name)
        # TODO make updating pipenv optional
        setup_pipenv(component_project_dir)
        component_agent_dir = create_aea_component_agent(component_project_dir, name)
        print_how_to_continue(component_agent_dir)


def print_how_to_continue(component_agent_dir: Path):
    print(
        f"Created a new aea '{component_agent_dir.name}' for the component"
        f" at aea project at {component_agent_dir.parent}")
    print("Run the following, to enable its virtual environment:")
    print(f"   `cd {component_agent_dir}`")
    print("   `alias aea=aea --registry-path $(realpath ../../../packages)`")
    print("   `pipenv shell`")
    print("The alias tells the aea cli to use the local registry at ./packages.")
    print("Now you can create an aea component there.")
    print("See `aea scaffold` for further information.")


def main(argv: List[Any]):
    check_python_version()
    if len(argv) < 2:
        print("Please provide a name to create a aea project for your new aea component")
        sys.exit(1)
    # TODO introduce intermediary command for creating an aea component agent
    scaffold_module(argv[1])


if __name__ == '__main__':
    main(sys.argv)
