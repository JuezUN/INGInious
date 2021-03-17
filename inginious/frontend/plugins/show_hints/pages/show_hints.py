import os

_SHOW_HINTS_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__),'templates')

def show_hints_tab(course, taskid, task_data, template_helper):

    tab_id = 'hints'
    link = '<i class="fa fa-question"></i>&nbsp; ' + _('Hints')

    template = template_helper.get_custom_renderer(_SHOW_HINTS_TEMPLATES_PATH, layout=False).hints_tab()

    return tab_id, link, template

def hints_modal(course, taskid, task_data, template_helper):

    return template_helper.get_custom_renderer(_SHOW_HINTS_TEMPLATES_PATH, layout=False).hints_edit_modal()
