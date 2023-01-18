import os
from collections import OrderedDict

_use_minified = True

JPLAG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "jplag.jar")

LANGUAGE_FILE_EXTENSION_MAP = {
    'c/c++': 'c',
    'java17': 'java',
    'python3': 'py',
    'text': 'txt',
}

LANGUAGE_PLAGIARISM_LANG_MAP = {
    'cpp11': 'c/c++',
    'cpp': 'c/c++',
    'c11': 'c/c++',
    'c': 'c/c++',
    'java7': 'java17',
    'java8': 'java17',
    'python3': 'python3',
    'vhdl': 'text',
    'verilog': 'text',
    'notebook': 'text'
}

ALLOWED_ENVIRONMENTS = {'multiple_languages', 'Notebook', 'Data Science', 'HDL'}

AVAILABLE_PLAGIARISM_LANGUAGES = OrderedDict(sorted([
    ("java8", "Java 8"),
    ("python3", "Python 3.9"),
    ("cpp", "C++/C++11"),
    ("c", "C/C11"),
    ("verilog", "Verilog"),
    ("vhdl", "VHDL"),
    ("notebook", "Jupyter notebook"),
], key=lambda x: x[0]))


def set_use_minified(use_minified):
    """ Define if use minified files """
    global _use_minified
    _use_minified = use_minified


def add_static_files(template_helper):
    if _use_minified:
        template_helper.add_css("/plagiarism/static/css/plagiarism.css")
    else:
        template_helper.add_css("/plagiarism/static/css/plagiarism.min.css")
