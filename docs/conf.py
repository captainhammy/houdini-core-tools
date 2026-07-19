"""Configure documentation for Sphinx."""

# Standard Library
import pathlib
import sys
from datetime import date

# Third Party
from dunamai import Pattern, Version
from sphinx_pyproject import SphinxConfig

sys.path.insert(0, pathlib.Path("../src/python").resolve().as_posix())

try:
    version = Version.from_git(Pattern.DefaultUnprefixed, strict=True).serialize()

except RuntimeError:
    version = "0.1.0"

config = SphinxConfig(
    "../pyproject.toml",
    globalns=globals(),
    config_overrides={"version": version}
)

project = config.name
copyright = f"{date.today().year}, {config.author}"


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
    "sphinx_copybutton",
    "enum_tools.autoenum",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "hou": ("https://www.sidefx.com/docs/houdini/hom/hou", "objects_hou.inv"),
}

autodoc_mock_imports = ["hou", "nodegraphtitle"]
autodoc_member_order = "bysource"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

nitpicky = True
nitpick_ignore = [
    ("py:const", "None"),
    ("py:class", "JSONValue")
]
