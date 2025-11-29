import logging


from portal_tool.installer.configurators.configurator import Configurator


class MacConfigurator(Configurator):
    def __init__(self):
        logging.info("Running MacOs configurator")

    def _try_install_vcpkg_dependencies(self) -> None:
        pass

    def _install_package(self, packages: list[str]) -> None:
        raise NotImplementedError

    def _get_script_extension(self) -> str:
        return "sh"

    def _get_executable_extension(self) -> str:
        return ""
