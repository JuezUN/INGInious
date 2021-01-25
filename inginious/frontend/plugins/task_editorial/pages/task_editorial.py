import os
import json

from collections import OrderedDict
from inginious.frontend.pages.course_admin.task_edit import CourseEditTask, CourseTaskFiles
from inginious.frontend.plugins.multilang.problems.languages import get_all_available_languages
from inginious.frontend.parsable_text import ParsableText

_TASK_EDITORIAL_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")

def editorial_task_tab(course, taskid, task_data, template_helper):

    tab_id = 'tab_editorial'
    link = '<i class="fa fa-graduation-cap fa-fw"></i>&nbsp; ' + _('Task editorial')

    editorial_task_data = ParsableText(add_editorial_task_data(task_data),"rst")

    content = template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH, layout=False).task_editorial(task_data, editorial_task_data, get_all_available_languages())
    return tab_id, link ,content

def editorial_task_preview(course, task, template_helper):

    content = template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH, layout=False).task_editorial_preview(course, task)

    return str(content)

def add_editorial_task_data(task_data):
    editorial_task_data = task_data.get("tutorial_description", {})
    if (editorial_task_data is False):
        editorial_task_data = {}
    return editorial_task_data

