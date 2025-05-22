import logging
import pathlib
import subprocess
import tempfile
import shlex
from portal_tool.models import GitDetails, PortalFramework
from portal_tool.singleton import Singleton


def get_main_ref(repo_path: pathlib.Path) -> str:
    main_ref = repo_path / ".git/refs/heads/main"
    if main_ref.is_file():
        with open(main_ref, "r") as main_ref_file:
            return main_ref_file.read().strip()
    logging.warning(f"Could not find main ref at {main_ref}")
    return "Invalid"

class GitManager(metaclass=Singleton):
    def __init__(self):
        self.framework_repo = "Invalid"
        self.head_ref = "main"
        self.registry_repo = "Invalid"
        self.temporary_folder = pathlib.Path(tempfile.mkdtemp())
        self.framework_ref = "Invalid"
        self.registry_ref = "Invalid"

    def init_repo(self, framework: PortalFramework) -> None:
        self.framework_repo = framework.repo
        self.registry_repo = framework.vcpkg_registry_repo
        framework_repo_url = f"https://github.com/{self.framework_repo}.git"
        registry_repo_url = f"https://github.com/{self.registry_repo}.git"

        subprocess.check_output(shlex.split(f"git clone {framework_repo_url} \"{self.temporary_folder / "framework"}\""))
        subprocess.check_output(shlex.split(f"git clone {registry_repo_url} \"{self.temporary_folder / "registry"}\""))

        self.framework_ref = get_main_ref(self.temporary_folder / "framework")
        self.registry_ref = get_main_ref(self.temporary_folder / "registry")
        logging.info(f"Got ref for {self.framework_repo}: {self.framework_ref}")
        logging.info(f"Got ref for {self.registry_repo}: {self.registry_ref}")

    def calculate_sha(self, port_name: str) -> str:
        sha = subprocess.check_output(
            shlex.split(f"git -C \"{self.temporary_folder / "registry" / "ports"}\" ls-tree --format='%(objectname)' HEAD -- {port_name} {self.framework_ref}"))
        logging.debug(f"Got sha for {port_name}: {sha}")
        return sha.strip().decode()

    def to_details(self, sha: str | None = None, port_name: str | None = None, subdirectory: str = "") -> GitDetails:
        if port_name and not sha:
            sha = self.calculate_sha(port_name)
        return GitDetails(
            repo=self.framework_repo,
            ref=self.framework_ref,
            head_ref=self.head_ref,
            sha=sha or "",
            subdirectory=subdirectory  # This will be filled out for each port
        )

    def get_version(self, subdirectory: str) -> str:
        version_file_path = pathlib.Path(self.temporary_folder) / "framework" / subdirectory / "version.txt"
        if version_file_path.is_file():
            with open(version_file_path, "r") as version_file:
                return version_file.read().strip()
        logging.warn(f"Could not find version file at {version_file_path}")
        return "0.0.0"