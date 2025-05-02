import pathlib
import typer

from portal_tool.git_manager import GitManager
from portal_tool.models import PortalFramework
from portal_tool.module import get_module_details_from_user, create_module_build_structure
from portal_tool.vcpkg_port import update_registry, generate_vcpkg_configuration

g_framework_path = pathlib.Path("framework.json")
framework: PortalFramework | None = None

registry = typer.Typer()

@registry.command()
def update(dest: pathlib.Path | None = typer.Argument(None, help="The output folder of the updated registry")) -> None:
    if not dest:
        dest = pathlib.Path.cwd()
    update_registry(dest, framework)

@registry.command()
def create_config(dest: pathlib.Path | None = typer.Argument(None, help="The output folder of the config")) -> None:
    if not dest:
        dest = pathlib.Path.cwd()
    generate_vcpkg_configuration(dest, framework)

module = typer.Typer()
@module.command()
def create(dest: pathlib.Path | None = typer.Argument(None, help="The output folder for the new module")):
    if not dest:
        dest = pathlib.Path.cwd()
    new_module = get_module_details_from_user(framework)
    create_module_build_structure(new_module, dest)
    framework.modules.append(new_module)
    with open(g_framework_path, "w") as framework_file:
        framework_file.write(framework.model_dump_json(indent=4))

    should_update_registry = typer.confirm("Would you like to update the registry?", default=True)
    if should_update_registry:
        registry_path = typer.prompt("Which folder would you like to update?", default=dest)
        update(pathlib.Path(registry_path))


app = typer.Typer()
app.add_typer(registry, name="registry", help="Commands for managing the registry")
app.add_typer(module, name="module", help="Commands for managing the modules")

@app.callback()
def main(
    framework_path: pathlib.Path = typer.Argument(help="The path to the json file containing the framework details"),
):
    global framework
    global g_framework_path
    g_framework_path = framework_path
    with open(framework_path) as framework_file:
        framework = PortalFramework.model_validate_json(framework_file.read())
    GitManager().init_repo(framework)



if __name__ == '__main__':
    app()
