import logging
import pathlib
import shlex
import subprocess

import jinja2

from portal_tool.git_manager import GitManager
from portal_tool.models import PortalModule, PortDetails, PortalFramework


def enhance_portal_module(module: PortalModule) -> PortDetails:
    git_manager = GitManager()
    git_details = git_manager.to_details(subdirectory=module.short_name)
    version = git_manager.get_version(module.short_name)

    return PortDetails(
        name=module.name,
        version=version,
        short_name=module.short_name,
        description=module.description,
        license="MIT",  # TODO: get from repo
        git=git_details,
        options=module.options,
        dependencies=[dep.model_dump() for dep in module.dependencies],
    )


def generate_vcpkg_port(details: PortDetails, output_path: pathlib.Path) -> None:
    env = jinja2.environment.Environment(
        loader=jinja2.PackageLoader("portal_tool", "templates/vcpkg"),
    )

    cmake_template = env.get_template("portfile.cmake.j2")
    cmake = cmake_template.render(port=details)
    vcpkg_template = env.get_template("vcpkg.json.j2")
    vcpkg = vcpkg_template.render(port=details)
    usage_template = env.get_template("usage.j2")
    usage = usage_template.render(port=details)

    port_path = output_path / "ports" / details.name
    if not port_path.exists():
        port_path.mkdir(parents=True)

    logging.info(f"Generating vcpkg port at: {port_path}")

    port_file = port_path / "portfile.cmake"
    vcpkg_file = port_path / "vcpkg.json"
    usage_file = port_path / "usage"

    port_file.write_text(cmake)
    vcpkg_file.write_text(vcpkg)
    usage_file.write_text(usage)

    subprocess.check_output(shlex.split(f'vcpkg format-manifest "{vcpkg_file}"'))


def generate_vcpkg_configuration(output_path: pathlib.Path, framework: PortalFramework):
    git_manager = GitManager()
    env = jinja2.environment.Environment(
        loader=jinja2.PackageLoader("portal_tool", "templates/vcpkg"),
    )
    template = env.get_template("vcpkg-configuration.json.j2")
    rendered = template.render(
        ports=framework.modules, registry_ref=git_manager.registry_commit
    )

    with open(output_path / "vcpkg-configuration.json", "w") as f:
        f.write(rendered)


def update_registry(output_path: pathlib.Path, framework: PortalFramework) -> None:
    logging.info(f"Updating vcpkg registry at: {output_path.absolute()}")
    GitManager().validate_modules_versions(framework.modules)
    for module in framework.modules:
        port = enhance_portal_module(module)
        generate_vcpkg_port(port, output_path)

    subprocess.check_output(
        shlex.split(
            f'vcpkg --x-builtin-ports-root="{output_path / "ports"}" --x-builtin-registry-versions-dir="{output_path / "versions"}" x-add-version --all --verbose'
        )
    )
