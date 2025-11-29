import abc
import os

import pathlib

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

    @abc.abstractmethod
    def _try_install_vcpkg(self) -> None:
        pass
