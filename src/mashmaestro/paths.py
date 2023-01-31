import importlib.resources as importlib_resources
import subprocess
from pathlib import Path

from mashmaestro import resources


def get_repo_checkout_path() -> Path:
    repo_checkout_path = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"]
    )
    repo_checkout_path = repo_checkout_path.decode("ascii").splitlines()[0]
    return Path(repo_checkout_path)


def find_resources(
    resources_package: importlib_resources.Package, resource_name: str
) -> Path:
    for entry in importlib_resources.files(resources_package).iterdir():
        if resource_name in entry.name:
            return entry


repo_path = get_repo_checkout_path()
bot3_pickle = find_resources(
    resources_package=resources, resource_name="bot3.pickle"
)  # has recipe name and url already
