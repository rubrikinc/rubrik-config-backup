# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath('../src'))


# -- Project information -----------------------------------------------------

project = 'Rubrik Configuration Backup'
copyright = '2020, Rubrik Inc'
author = 'Ramzi Ferchichi'

# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'recommonmark',
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


source_suffix = ['.rst', '.md']


pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'
html_favicon = "_static/rubrik.ico"
html_logo = "_static/rubrik.png"

html_theme_options = {
    "external_links": [],
    "github_url": "https://github.com/rubrikinc",
    "twitter_url": "https://twitter.com/rubrikinc",
    #"google_analytics_id": "",
}

#html_theme_options = {
#    'logo': 'rubrik.png',
#    'logo_name': True,
#    'github_button': True,
#    'github_user': 'rubrikinc',
#    'github_repo': 'rubrik-config-backup'
#}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']