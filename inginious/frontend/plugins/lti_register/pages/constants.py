_use_minified = True


def set_use_minified(use_minified):
    """ Define if use minified files """
    global _use_minified
    _use_minified = use_minified


def use_minified():
    """ return a boolean to define if use minified files """
    return _use_minified