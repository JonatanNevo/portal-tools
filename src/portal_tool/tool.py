import logging
import pathlib
from typing import Annotated

import appdirs
import typer

from portal_tool.git_manager import GitManager
from portal_tool.models import PortalFramework
from portal_tool.vcpkg_port import update_registry, generate_vcpkg_configuration

global_working_directory = pathlib.Path.cwd()
framework: PortalFramework

registry = typer.Typer()


@registry.command()
def update() -> None:
    update_registry(global_working_directory, framework)


@registry.command()
def create_config() -> None:
    generate_vcpkg_configuration(global_working_directory, framework)


def sync_framework_data(*args, **kwargs) -> None:
    user_data_path = pathlib.Path(appdirs.user_data_dir("portal-tool"))
    (user_data_path / "framework.json").write_text(framework.model_dump_json(indent=4))


app = typer.Typer(result_callback=sync_framework_data)
app.add_typer(registry, name="registry", help="Commands for managing the registry")


@app.callback()
def main(
    working_dir: Annotated[
        pathlib.Path,
        typer.Option(
            "-d", "--working-dir", help="The working directory of the project"
        ),
    ] = pathlib.Path.cwd(),
    framework_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "-f", "--framework-path", help="The path to the framework.json file"
        ),
    ] = None,
    force_update_framework: Annotated[
        bool,
        typer.Option(
            "-u", "--force-update-framework", help="Force update the framework"
        ),
    ] = False,
):
    global framework
    global global_working_directory
    global_working_directory = working_dir

    logging.basicConfig(level=logging.INFO)

    user_data_path = pathlib.Path(appdirs.user_data_dir("portal-tool"))

    if framework_path is not None:
        framework = PortalFramework.model_validate_json(framework_path.read_text())
    elif (working_dir / "framework.json").exists() and not force_update_framework:
        framework = PortalFramework.model_validate_json(
            (working_dir / "framework.json").read_text()
        )
    elif (user_data_path / "framework.json").exists() and not force_update_framework:
        framework = PortalFramework.model_validate_json(
            (user_data_path / "framework.json").read_text()
        )
    else:
        # TODO: get from git as well?
        raise FileNotFoundError(
            "No framework.json found in working directory or user data directory"
        )

    GitManager().init_repo(framework)


if __name__ == "__main__":
    app()
