import os

from inginious.frontend.pages.course_admin.task_edit import CourseEditTask

_SHOW_HINTS_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__),'templates')

def show_hints_tab(course, taskid, task_data, template_helper):

    tab_id = 'hints'
    link = '<i class="fa fa-question"></i>&nbsp; ' + _('Hints')

    add_static_files(template_helper)

    #Get task data
    task_hints = task_data.get("task_hints")

    if task_data.get("task_hints") is None:
        task_hints = {}

    template = template_helper.get_custom_renderer(_SHOW_HINTS_TEMPLATES_PATH, layout=False).hints_tab(task_hints)

    return tab_id, link, template

def hints_modal(course, taskid, task_data, template_helper):

    return template_helper.get_custom_renderer(_SHOW_HINTS_TEMPLATES_PATH, layout=False).hints_edit_modal()


def add_static_files(template_helper):

    template_helper.add_javascript("/task_editorial/static/show_hints.js")


def on_task_submit(course, taskid, task_data, task_fs):

    task_data["task_hints"] = CourseEditTask.dict_from_prefix("task_hints",task_data)
