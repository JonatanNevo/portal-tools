import logging


from portal_tool.installer.configurators.configurator import Configurator


class LinuxConfigurator(Configurator):
    def __init__(self):
        logging.info("Running Ubuntu configurator")

    def _get_script_extension(self) -> str:
        return "sh"
