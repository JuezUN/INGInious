import os
import json

_TASK_TUTORIAL_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")

def tutorial_tab(course, taskid, task_data, template_helper):

    tab_id = 'tab_tutorial'
    link = '<i class="fa fa-list-ul fa-fw"></i>&nbsp; ' + _('Tutorial')
    content = template_helper.get_custom_renderer(_TASK_TUTORIAL_TEMPLATE_PATH, layout=False).task_tutorial(taskid)
    return tab_id, link ,content
