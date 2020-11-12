import os
from inginious.frontend.plugins.utils import create_static_resource_page

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def header(template_helper):
    return str(template_helper.get_custom_renderer('frontend/plugins/UN_template', layout=False).header("UNCode"))


def footer(template_helper):
    return str(template_helper.get_custom_renderer('frontend/plugins/UN_template', layout=False).footer())


def init(plugin_manager, course_factory, client, config):
    plugin_manager.add_page(r'/UN_template/static/(.*)', create_static_resource_page(_static_folder_path))

    use_minified = config.get("use_minified", True)
    if use_minified:
        plugin_manager.add_hook("css", lambda: "/UN_template/static/css/UN_template.min.css")
        plugin_manager.add_hook("javascript_footer", lambda: "/UN_template/static/js/unal.min.js")
    else:
        plugin_manager.add_hook("javascript_footer", lambda: "/UN_template/static/js/unal.js")
        plugin_manager.add_hook("css", lambda: "/UN_template/static/css/reset.css")
        plugin_manager.add_hook("css", lambda: "/UN_template/static/css/unal.css")
        plugin_manager.add_hook("css", lambda: "/UN_template/static/css/base.css")
        plugin_manager.add_hook("css", lambda: "/UN_template/static/css/tablet.css")
        plugin_manager.add_hook("css", lambda: "/UN_template/static/css/phone.css")
        plugin_manager.add_hook("css", lambda: "/UN_template/static/css/small.css")
        plugin_manager.add_hook("css", lambda: "/UN_template/static/css/printer.css")
        plugin_manager.add_hook("css", lambda: "/UN_template/static/css/new_unal.css")
    plugin_manager.add_hook("css", lambda: "/UN_template/static/icons/elusive/css/elusive-icons.min.css")
    plugin_manager.add_hook('body_header', header)
    plugin_manager.add_hook('body_footer', footer)
