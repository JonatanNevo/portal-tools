from portal_tool.installer.configurator_factory import ConfiguratorFactory


class Installer:
    def __init__(self, examples_url: str, registry_url: str):
        self.examples_url = examples_url
        self.registry_url = registry_url

    def install(self) -> None:
        configurator = ConfiguratorFactory().create()
        configurator.configure_vcpkg()
        configurator.configure_build_environment()
