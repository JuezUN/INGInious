import os
from collections import OrderedDict

JPLAG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "jplag.jar")

LANGUAGE_FILE_EXTENSION_MAP = {
    'c/c++': 'cpp',
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
    ("java7", "Java 7"),
    ("java8", "Java 8"),
    ("python3", "Python 3.6"),
    ("cpp", "C++/C++11"),
    ("c", "C/C11"),
    ("verilog", "Verilog"),
    ("vhdl", "VHDL"),
    ("notebook", "Jupyter notebook"),
], key=lambda x: x[0]))

_use_minfied = True


def set_use_minified(value):
    global _use_minfied
    _use_minfied = value


def use_minified():
    return _use_minfied
