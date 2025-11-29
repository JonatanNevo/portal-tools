import logging
import enum
import platform
import subprocess

import typer

from portal_tool.installer.configurators.configurator import Configurator


class UbuntuDistro(enum.Enum):
    Debian = enum.auto()
    Fedora = enum.auto()


class LinuxConfigurator(Configurator):
    def __init__(self):
        logging.info("Running Ubuntu configurator")
        uname_version = platform.version()

        if "ubuntu" in uname_version.lower() or "debian" in uname_version.lower():
            self.distro = UbuntuDistro.Debian
        elif "fedora" in uname_version.lower():
            self.distro = UbuntuDistro.Fedora
        else:
            typer.Abort(f"Unsupported Linux distribution: {uname_version}")

    def _try_install_vcpkg_dependencies(self) -> None:
        self._install_package(["curl", "zip", "unzip", "tar"])

    def _install_package(self, packages: list[str]) -> None:
        if self.distro == UbuntuDistro.Debian:
            subprocess.check_call(["sudo", "apt-get", "install", *packages])
        else:
            subprocess.check_call(["sudo", "dnf", "install", *packages])

    def _get_script_extension(self) -> str:
        return "sh"

    def _get_executable_extension(self) -> str:
        return ""
