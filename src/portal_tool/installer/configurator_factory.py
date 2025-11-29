import platform
from dataclasses import dataclass

from portal_tool.installer.configurators.configurator_protocol import Configurator
from portal_tool.installer.configurators.linux_configurator import UbuntuConfigurator
from portal_tool.installer.configurators.mac_configurator import MacConfigurator
from portal_tool.installer.configurators.windows_configurator import WindowsConfigurator


@dataclass(frozen=True)
class PlatformDetails:
    name: str
    version: str


class ConfiguratorFactory:
    def __init__(self):
        self.configurators = {
            "Windows": {"11": WindowsConfigurator},
            "Linux": {"Ubuntu": UbuntuConfigurator},
            "Darwin": {  # Mac does not have the mac version in `platform.version` for some reason
                "Darwin": MacConfigurator
            },
        }

    def create(self) -> Configurator:
        local_details = PlatformDetails(platform.system(), str(platform.release()))

        system_configurators = self.configurators.get(local_details.name)
        if system_configurators is None:
            raise ValueError(f"Unsupported platform: {local_details.name}")

        configurator_class = system_configurators.get(local_details.version)
        if configurator_class is None:
            raise ValueError(
                f"Unsupported version: {local_details.version} for system: {local_details.name}."
            )

        return configurator_class()
