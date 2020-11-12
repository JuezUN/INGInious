def base_renderer_path():
    return 'frontend/plugins/statistics/pages'


_use_minfied = True


def set_use_minified(value):
    global _use_minfied
    _use_minfied = value


def get_use_minified():
    return _use_minfied
