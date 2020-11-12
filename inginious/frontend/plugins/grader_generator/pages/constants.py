import os

_BASE_RENDERER_PATH = os.path.dirname(__file__)
BASE_TEMPLATE_FOLDER = os.path.join(_BASE_RENDERER_PATH, "templates")
_use_minified = True


def set_use_minified(value):
    global _use_minified
    _use_minified = value


def get_use_minified():
    return _use_minified
