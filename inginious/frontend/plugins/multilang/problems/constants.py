_python_tutor_url = "http://localhost:8003/"
_linter_url = "http://localhost:4567/"
_show_tools = True
_use_minified = True
_use_wavedrom = True


def set_python_tutor_url(new_python_tutor_url):
    global _python_tutor_url
    _python_tutor_url = new_python_tutor_url


def set_linter_url(new_linter_url):
    global _linter_url
    _linter_url = new_linter_url


def set_show_tools(new_show_tools_value):
    global _show_tools
    _show_tools = new_show_tools_value


def set_use_minified(use_minified):
    global _use_minified
    _use_minified = use_minified


def set_use_wavedrom(use_wavedrom):
    global _use_wavedrom
    _use_wavedrom = use_wavedrom


def get_python_tutor_url():
    return _python_tutor_url


def get_linter_url():
    return _linter_url


def get_show_tools():
    return _show_tools


def add_static_files(template_helper):
    template_helper.add_javascript("https://cdn.jsdelivr.net/npm/marked/marked.min.js")
    template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/prism/1.19.0/components/prism-core.min.js")
    template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/prism/1.19.0/components/prism-python.min.js")
    template_helper.add_css("https://cdnjs.cloudflare.com/ajax/libs/prism/1.19.0/themes/prism.min.css")
    if _use_minified:
        template_helper.add_javascript("/multilang/static/notebook_renderer.min.js")
        template_helper.add_javascript("/multilang/static/multilang.min.js")
        template_helper.add_css("/multilang/static/multilang.min.css")
    else:
        template_helper.add_javascript("/multilang/static/notebook_renderer.js")
        template_helper.add_javascript("/multilang/static/multilang.js")
        template_helper.add_javascript("/multilang/static/grader.js")
        template_helper.add_css("/multilang/static/multilang.css")

    if _show_tools:
        if _use_minified:
            template_helper.add_javascript("/multilang/static/tools.min.js")
            template_helper.add_css("/multilang/static/tools.min.css")
        else:
            template_helper.add_javascript("/multilang/static/pythonTutor.js")
            template_helper.add_javascript("/multilang/static/codemirror_linter.js")
            template_helper.add_javascript("/multilang/static/lint.js")
            template_helper.add_javascript("/multilang/static/custom_input.js")
            template_helper.add_css("/multilang/static/lint.css")

    if _use_wavedrom:
        template_helper.add_javascript("https://wavedrom.com/skins/default.js")
        template_helper.add_javascript("https://wavedrom.com/wavedrom.min.js")

        if _use_minified:
            template_helper.add_javascript("/multilang/static/hdlgrader.min.js")
        else:
            template_helper.add_javascript("/multilang/static/hdlgrader.js")
