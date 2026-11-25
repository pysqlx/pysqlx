"""Sphinx configuration for the pysqlx documentation."""

import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _dist_version

from pysqlx.clients import IClient
from pysqlx.structures import Column, Table

# -- Project information ------------------------------------------------------

project = "pysqlx"
author = "Bassem Girgis"
copyright = "2022 pysqlx"

try:
    release = _dist_version("pysqlx")
except PackageNotFoundError as exc:  # pragma: no cover
    raise RuntimeError(
        "pysqlx must be installed to build the documentation; "
        "run `uv sync --dev` (or `pip install .`) first."
    ) from exc

version = ".".join(release.split(".")[:2])

# -- General configuration ----------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

source_suffix = {".rst": "restructuredtext"}
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Report every broken cross-reference.
nitpicky = True

autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Some modules import these classes for type checking only, to avoid import
# cycles. Give them the classes here, so that autodoc can resolve their type
# hints.
for _module_name, _module in list(sys.modules.items()):
    if _module_name.startswith("pysqlx."):
        for _class in (Column, IClient, Table):
            if not hasattr(_module, _class.__name__):
                setattr(_module, _class.__name__, _class)

# Generate the API reference pages from the autosummary directives.
autosummary_generate = True
templates_path = ["_templates"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Options for HTML output --------------------------------------------------

# Furo follows the system color scheme and lets the reader switch between the
# light and dark themes.
html_theme = "furo"
html_title = f"pysqlx {release}"
html_static_path = ["_static"]
html_logo = "_static/logo.svg"
html_favicon = "_static/logo.svg"
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#4f46e5",
        "color-brand-content": "#4f46e5",
    },
    "dark_css_variables": {
        "color-brand-primary": "#a5b4fc",
        "color-brand-content": "#a5b4fc",
    },
    "source_repository": "https://github.com/pysqlx/pysqlx/",
    "source_branch": "master",
    "source_directory": "docs/",
}
pygments_style = "default"
pygments_dark_style = "monokai"
htmlhelp_basename = "pysqlxdoc"

# -- Options for other builders -----------------------------------------------

latex_documents = [
    (
        master_doc,
        "pysqlx.tex",
        "pysqlx Documentation",
        author,
        "manual",
    )
]

man_pages = [(master_doc, "pysqlx", "pysqlx Documentation", [author], 1)]

texinfo_documents = [
    (
        master_doc,
        "pysqlx",
        "pysqlx Documentation",
        author,
        "pysqlx",
        "A generic SQL driver package.",
        "Miscellaneous",
    )
]
