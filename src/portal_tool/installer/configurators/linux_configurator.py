import logging
import enum
import platform
import re
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
        typer.echo("Installing vcpkg dependencies... (curl, zip, unzip, tar)")
        self._install_package(["curl", "zip", "unzip", "tar"])

    def _install_package(self, packages: list[str]) -> None:
        if self.distro == UbuntuDistro.Debian:
            subprocess.check_call(["sudo", "apt-get", "install", *packages])
        else:
            subprocess.check_call(["sudo", "dnf", "install", *packages])

    def _validate_compilers(self) -> None:
        typer.echo("Validating compilers...")

        clang_valid = False
        gcc_valid = False

        # Check for Clang 19+
        try:
            result = subprocess.run(
                ["clang", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                match = re.search(r"clang version (\d+)\.(\d+)", result.stdout)
                if match:
                    major = int(match.group(1))
                    if major >= 19:
                        # Try to get installation path
                        path_result = subprocess.run(
                            ["which", "clang"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        install_path = (
                            path_result.stdout.strip()
                            if path_result.returncode == 0
                            else "unknown"
                        )
                        typer.echo(
                            f"Clang {major}.{match.group(2)} found ({install_path})"
                        )
                        clang_valid = True
                    else:
                        typer.echo(
                            f"Clang {major}.{match.group(2)} found, but version 19+ is required"
                        )
        except (subprocess.SubprocessError, FileNotFoundError):
            typer.echo("Clang not found")

        # Check for gcc 15+
        try:
            result = subprocess.run(
                ["gcc", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Parse version from output like "gcc (GCC) X.Y.Z" or "gcc version X.Y.Z"
                match = re.search(r"gcc.*?(\d+)\.(\d+)", result.stdout, re.IGNORECASE)
                if match:
                    major = int(match.group(1))
                    if major >= 15:
                        # Try to get installation path
                        path_result = subprocess.run(
                            ["which", "gcc"], capture_output=True, text=True, timeout=5
                        )
                        install_path = (
                            path_result.stdout.strip()
                            if path_result.returncode == 0
                            else "unknown"
                        )
                        typer.echo(
                            f"gcc {major}.{match.group(2)} found ({install_path})"
                        )
                        gcc_valid = True
                    else:
                        typer.echo(
                            f"gcc {major}.{match.group(2)} found, but version 15+ is required"
                        )
        except (subprocess.SubprocessError, FileNotFoundError):
            typer.echo("gcc not found")

        # Require at least one valid compiler
        if not clang_valid and not gcc_valid:
            typer.echo("\nNo valid compiler found!")
            typer.echo("Please install at least one of the following:")
            typer.echo("  - Clang 19 or later")
            typer.echo("  - gcc 15 or later")
            raise typer.Abort("Compiler validation failed")

        typer.echo("Compiler validation successful!")

    def _get_script_extension(self) -> str:
        return "sh"

    def _get_executable_extension(self) -> str:
        return ""
