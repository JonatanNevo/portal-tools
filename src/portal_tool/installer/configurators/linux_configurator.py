import logging

import pathlib
import shlex
import subprocess

import appdirs
import typer

from portal_tool.installer.configurators.configurator import Configurator


class LinuxConfigurator(Configurator):
    def __init__(self):
        logging.info("Running Ubuntu configurator")

    def _try_install_vcpkg(self) -> None:
        install_vcpkg = typer.confirm("Would you like to install vcpkg?")
        if not install_vcpkg:
            raise typer.Abort(
                "No vcpkg installation, please install it manually and try again."
            )

        installation = pathlib.Path(
            typer.prompt(
                "Choose installation directory:", default=appdirs.user_data_dir()
            )
        )
        if not installation.exists():
            installation.mkdir(parents=True)

        vcpkg_directory = installation / "vcpkg"
        typer.echo(f"Cloning into: {vcpkg_directory}...")

        subprocess.check_output(
            shlex.split(
                f'git clone https://github.com/microsoft/vcpkg "{vcpkg_directory}"'
            )
        )
        typer.echo("Bootstrap vcpkg...")
        subprocess.check_output(shlex.split(f"{vcpkg_directory}/bootstrap-vcpkg.sh"))
