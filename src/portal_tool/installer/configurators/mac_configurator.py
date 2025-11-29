import logging


from portal_tool.installer.configurators.configurator import Configurator


class MacConfigurator(Configurator):
    def __init__(self):
        logging.info("Running MacOs configurator")

    def _get_script_extension(self) -> str:
        return "sh"
