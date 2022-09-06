from collections import OrderedDict


def get_all_available_languages():
    _available_language = {
        "java8": "Java 8",
        "python3": "Python 3.9",
        "cpp": "C++",
        "cpp11": "C++11",
        "c": "C",
        "c11": "C11",
        "verilog": "Verilog",
        "vhdl": "VHDL"
    }

    _available_languages = OrderedDict(sorted(_available_language.items()))
    return _available_languages
