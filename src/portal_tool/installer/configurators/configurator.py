import abc
import os

import pathlib
import shlex
import shutil
import subprocess

import typer


def find_vcpkg_root() -> pathlib.Path | None:
    value = os.environ.get("VCPKG_ROOT")
    return pathlib.Path(value) if value else None


class Configurator(metaclass=abc.ABCMeta):
    def configure_vcpkg(self) -> None:
        typer.echo("Configuring vcpkg...")
        root = find_vcpkg_root()
        if root is None:
            typer.echo("Failed to find global vcpkg.")
            self._try_install_vcpkg()
        else:
            typer.echo(f"Global vcpkg found at: {root}")

    def _try_install_vcpkg(self) -> None:
        install_vcpkg = typer.confirm("Would you like to install vcpkg?")
        if not install_vcpkg:
            raise typer.Abort(
                "No vcpkg installation, please install it manually and try again."
            )

        self._try_install_vcpkg_dependencies()

        installation_directory = pathlib.Path(
            typer.prompt(
                "Choose installation directory:",
                default=os.path.join(os.path.expanduser("~"), ".vcpkg"),
            )
        )
        if installation_directory.exists():
            override = typer.confirm("Folder exists, overwrite?")
            if not override:
                raise typer.Abort("Installation aborted.")
            shutil.rmtree(installation_directory)

        subprocess.check_output(
            shlex.split(
                f'git clone https://github.com/microsoft/vcpkg "{installation_directory}"'
            )
        )
        typer.echo("Bootstrap vcpkg...")
        subprocess.check_output(
            shlex.split(
                f"{installation_directory}/bootstrap-vcpkg.{self._get_script_extension()}"
            )
        )

    @abc.abstractmethod
    def _try_install_vcpkg_dependencies(self) -> None:
        pass

    @abc.abstractmethod
    def _get_script_extension(self) -> str:
        pass

    @abc.abstractmethod
    def _install_package(self, packages: list[str]) -> None:
        pass
