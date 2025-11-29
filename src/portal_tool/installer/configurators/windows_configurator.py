import logging


from portal_tool.installer.configurators.configurator import Configurator


class WindowsConfigurator(Configurator):
    def __init__(self):
        logging.info("Running Windows 11 configurator")

    def _get_script_extension(self) -> str:
        return "bat"
