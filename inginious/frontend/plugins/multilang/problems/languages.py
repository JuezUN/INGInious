from collections import OrderedDict


def get_available_languages():
    _available_language = {
        "java7": "Java 7",
        "java8": "Java 8",
        "python2": "Python 2.7",
        "python3": "Python 3.5",
        "cpp": "C++",
        "cpp11": "C++11",
        "c": "C",
        "c11": "C11",
        "verilog": "Verilog",
        "vhdl": "VHDL"
    }

    _available_languages = OrderedDict(sorted(_available_language.items()))
    return _available_languages
