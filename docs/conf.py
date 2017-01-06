# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bndl_elastic.__version__
import sphinx_rtd_theme


# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinxcontrib.programoutput',
]

templates_path = ['templates']
source_suffix = '.rst'
master_doc = 'index'

project = 'bndl-elastic'
copyright = '2016, Frens Jan Rumph'
author = 'Frens Jan Rumph'

version = '.'.join(map(str, bndl_elastic.__version__.info[:2]))
release = bndl_elastic.__version__.version

language = 'en'
exclude_patterns = ['build']

pygments_style = 'sphinx'
todo_include_todos = True

# -- Options for autodoc --------------------------------------------------
autodoc_member_order = 'bysource'
autodoc_default_flags = ['members', 'show-inheritance']

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['static']
htmlhelp_basename = 'bndl_elastic_doc'
