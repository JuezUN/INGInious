import os
from collections import OrderedDict
from inginious.frontend.pages.course_admin.task_edit import CourseEditTask

_SHOW_HINTS_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__),'templates')

def edit_hints_tab(course, taskid, task_data, template_helper):

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
    template_helper.add_javascript("/show_hints/static/hints_edit.js")

def on_task_submit(course, taskid, task_data, task_fs):

    task_data["task_hints"] = CourseEditTask.dict_from_prefix("task_hints",task_data)

    #Delete key for hint template if it exists
    if "hid" in task_data["task_hints"].keys():
        del task_data["task_hints"]["hid"]

    #Delete duplicate items if they exists

    fields_to_delete = []

    for key in task_data:
        if "task_hints[" in key:
            fields_to_delete.append(key)

    for key in fields_to_delete:
        del task_data[key]

    hints_to_delete = []

    #Delete items that have empty mandatory fields

    for hint_id in task_data["task_hints"]:
        if task_data["task_hints"][hint_id] and task_data["task_hints"][hint_id]["content"] is None:
            hints_to_delete.append(hint_id)

        if task_data["task_hints"][hint_id] and task_data["task_hints"][hint_id]["title"] is None:
            hints_to_delete.append(hint_id)

    for hint_id in hints_to_delete:
        del task_data["task_hints"][hint_id]

    task_data["task_hints"] = OrderedDict(sorted(task_data["task_hints"].items()))

def update_ordered_hints(hints):

    new_hint_list = {}
    for hint in hints:
        new_hint_list.append(hint)

    return new_hint_list
