_python_tutor_url = "http://localhost:8003/"
_python_tutor_py2_url = "http://localhost:8004/"
_linter_url = "http://localhost:4567/"
_show_tools = True


def set_python_tutor_url(new_python_tutor_url):
    global _python_tutor_url
    _python_tutor_url = new_python_tutor_url


def set_python_tutor_py2_url(new_python_tutor_py2_url):
    """
    Use a separate python tutor url that only will manage Python 2 visualizations.
    This is necessary as PythonTutor by default only builds wither for python3 or python 2.
    Thus, two separate PythonTutors have to be deployed.
    """
    global _python_tutor_py2_url
    _python_tutor_py2_url = new_python_tutor_py2_url


def set_linter_url(new_linter_url):
    global _linter_url
    _linter_url = new_linter_url


def set_show_tools(new_show_tools_value):
    global _show_tools
    _show_tools = new_show_tools_value


def get_python_tutor_url():
    return _python_tutor_url


def get_linter_url():
    return _linter_url


def get_show_tools():
    return _show_tools


def get_python_tutor_py2_url():
    return _python_tutor_py2_url
