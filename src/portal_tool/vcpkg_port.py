import logging
import pathlib
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

    with open(port_path / "portfile.cmake", "w") as f:
        f.write(cmake)
    with open(port_path / "vcpkg.json", "w") as f:
        f.write(vcpkg)
    with open(port_path / "usage", "w") as f:
        f.write(usage)


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
    for module in framework.modules:
        port = enhance_portal_module(module)
        generate_vcpkg_port(port, output_path)
