from pydantic import BaseModel, Field

class GitDetails(BaseModel):
    repo: str
    ref: str
    sha: str
    head_ref: str
    subdirectory: str


class Dependency(BaseModel):
    name: str
    version: str
    features: list[str] = Field(default_factory=list)
    target: str | None


class PortDetails(BaseModel):
    name: str
    short_name: str
    version: str
    description: str
    license: str
    git: GitDetails
    options: list[str]
    dependencies: list[Dependency]


class PortalModule(BaseModel):
    name: str
    subdirectory: str
    description: str
    build_options: list[str] = Field(default_factory=list)
    short_name: str
    dependencies: list[Dependency] = Field(default_factory=list)


class PortalFramework(BaseModel):
    repo: str
    vcpkg_registry_repo: str
    modules: list[PortalModule] = Field(default_factory=list)
