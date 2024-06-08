import os
import sys
import django


# Ustawienie ścieżki do katalogu projektu
sys.path.insert(0, os.path.abspath('../../'))

# Ustawienie zmiennej środowiskowej DJANGO_SETTINGS_MODULE
os.environ['DJANGO_SETTINGS_MODULE'] = 'przewodnik_po_miescie.settings'

# Inicjalizacja Django
django.setup()

# -- Project information -----------------------------------------------------

project = 'Przewodnik po mieście'
author = 'Łukasz Kotowski, Dominik Gąsowski, Wojciech Domański, Jakub Kazimiruk'
copyright = 'Łukasz Kotowski, Dominik Gąsowski, Wojciech Domański, Jakub Kazimiruk'
release = '1.0.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]



templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

