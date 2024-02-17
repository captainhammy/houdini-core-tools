"""Package definition file for houdini_core_tools."""

name = "houdini_core_tools"

description = "Houdini Core Tools"


@early()
def version() -> str:
    """Get the package version.

    Because this project is not versioned we'll just use the short git hash as the version.

    Returns:
        The package version.
    """
    import subprocess

    try:
        output = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])

    except subprocess.CalledProcessError:
        return "0.1.0"

    return output.decode("utf-8").strip()


authors = ["graham thompson"]

requires = [
    "houdini",
    "python_singleton",
]

build_system = "cmake"

tests = {
    "unit": {
        "command": "hython -m pytest tests",
        "requires": ["pytest", "pytest_cov", "pytest_houdini", "pytest_mock"],
    }
}


def commands():
    """Run commands on package setup."""
    env.PYTHONPATH.prepend("{root}/python")

    env.HOUDINI_PATH.prepend("{root}/houdini")
