import pathlib

import jinja2
import typer

from portal_tool.models import PortalModule, Dependency, PortalFramework
from portal_tool.vcpkg_port import enhance_portal_module


def get_module_details_from_user(framework: PortalFramework) -> PortalModule:
    name = typer.prompt("Module name", "")
    if name in [m.name for m in framework.modules]:
        raise ValueError(f"Module {name} already exists in the framework.")
    try:
        default_sub = name.split("-")[1]
        default_short_name = name.split("-")[1]
    except Exception:
        default_sub = name
        default_short_name = name

    description = typer.prompt("Module description", "")
    subdirectory = typer.prompt(f"Module subdirectory", default_sub)
    short_name = typer.prompt(f"Module short name", default_short_name)
    build_options = typer.prompt("Module build options (separated by commas)",
                                 "PORTAL_FIND_PACAKGE=ON").split(",")
    if build_options[0] == "":
        build_options = []

    dependencies = []
    yes_no = typer.confirm("Would you like to add dependencies?", default=False)
    while yes_no:
        dep_name = typer.prompt("Dependency name", "")
        for module in framework.modules:
            if dep_name == module.name:
                port = enhance_portal_module(framework, module)
                default_version = port.version
                default_target = "portal::" + port.short_name
                break
        else:
            default_version = "0.0.1"
            default_target = f"{dep_name}::{dep_name}"

        dep_version = typer.prompt("Dependency version", default_version)
        dep_features = typer.prompt("Dependency features (separated by commas)", "").split(",")
        dep_target = typer.prompt("Dependency target", default_target)
        if dep_features[0] == "":
            dep_features = []
        dependencies.append(
            Dependency(
                name=dep_name,
                version=dep_version,
                features=dep_features,
                target=dep_target
            )
        )
        yes_no = typer.confirm("Would you like to add another dependency?", default=False)
    return PortalModule(
        name=name,
        subdirectory=subdirectory,
        description=description,
        build_options=build_options,
        short_name=short_name,
        dependencies=dependencies
    )


def create_module_build_structure(module: PortalModule, sources_root: pathlib.Path) -> None:
    env = jinja2.environment.Environment(
        loader=jinja2.PackageLoader("portal_tool", "templates/module"),
    )
    cmake_template = env.get_template("CMakeLists.txt.j2")
    cmake_lists = cmake_template.render(
        module=module,
        dependencies=[dep for dep in module.dependencies if not dep.name.startswith("portal")],
        portal_dependencies=[dep for dep in module.dependencies if dep.name.startswith("portal")],
        default_sources=True,
        special_cmake=None
    )

    cmake_config_template = env.get_template("config.cmake.in.j2")
    cmake_config = cmake_config_template.render(
        module=module
    )

    module_path = sources_root / module.subdirectory
    if not module_path.exists():
        module_path.mkdir(parents=True)

    with open (module_path / "CMakeLists.txt", "w") as f:
        f.write(cmake_lists)

    with open (module_path / "version", "w") as f:
        f.write("0.0.1")

    module_sources_path = module_path / "portal" / module.subdirectory
    if not module_sources_path.exists():
        module_sources_path.mkdir(parents=True)

    cmake_path = sources_root / "cmake"
    if not cmake_path.exists():
        cmake_path.mkdir(parents=True)

    with open (cmake_path / f"{module.name}-config.cmake", "w") as f:
        f.write(cmake_config)