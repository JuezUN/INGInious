import os
import uuid
import json

from collections import OrderedDict
from inginious.frontend.pages.course_admin.task_edit import CourseEditTask
from .constants import use_minified

_SHOW_HINTS_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')


def edit_hints_tab(course, taskid, task_data, template_helper):
    tab_id = 'hints'
    link = '<i class="fa fa-question"></i>&nbsp; ' + _('Hints')

    add_static_files(template_helper)

    # Get task data
    task_hints = task_data.get("task_hints", {})

    render = template_helper.get_custom_renderer(_SHOW_HINTS_TEMPLATES_PATH, layout=False)

    template = str(render.hints_tab(task_hints)) + str(render.hint_row_table_template())

    return tab_id, link, template


def get_hints_edit_modal_template(course, taskid, task_data, template_helper):
    return template_helper.get_custom_renderer(_SHOW_HINTS_TEMPLATES_PATH, layout=False).hints_edit_modal()


def add_static_files(template_helper):
    if use_minified():
        template_helper.add_javascript("/task_hints/static/js/hints_edit.min.js")
    else:
        template_helper.add_javascript("/task_hints/static/js/hints_edit.js")


def on_task_submit(course, taskid, task_data, task_fs):
    task_data["task_hints"] = CourseEditTask.dict_from_prefix("task_hints", task_data)

    # Delete key for hint template if it exists
    if "KEY" in task_data["task_hints"].keys():
        del task_data["task_hints"]["KEY"]

    # Delete duplicate items if they exists

    fields_to_delete = []

    for key in task_data:
        if "task_hints[" in key:
            fields_to_delete.append(key)

    for key in fields_to_delete:
        del task_data[key]

    # Check the fields for each hint in task

    for hint_id in task_data["task_hints"]:
        if not task_data["task_hints"][hint_id]["content"]:
            return json.dumps({"status": "error", "message": _("Some hints in task have empty content fields.")})

        if not task_data["task_hints"][hint_id]["title"]:
            return json.dumps({"status": "error", "message": _("Some hints in task have empty title fields.")})

        penalty = task_data["task_hints"][hint_id]["penalty"]
        if penalty and (float(penalty) < 0 or 100 < float(penalty)):
            return json.dumps({"status": "error", "message": _("Penalty for hints must be between 0.0% and 100.0%.")})

        elif not penalty:
            task_data["task_hints"][hint_id]["penalty"] = '0.0'

        else:
            task_data["task_hints"][hint_id]["penalty"] = round(float(penalty),1)

    # Add id for hints
    task_data["task_hints"] = set_hints_id(task_data["task_hints"])
    task_data["task_hints"] = OrderedDict(sorted(task_data["task_hints"].items()))


def set_hints_id(task_hints):
    for key in task_hints:
        if not task_hints[key]["id"]:
            task_hints[key]["id"] = str(uuid.uuid4())
    return task_hints
