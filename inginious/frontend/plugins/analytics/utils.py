_use_minfied = True


def set_use_minified(value):
    global _use_minfied
    _use_minfied = value


def use_minified():
    return _use_minfied
