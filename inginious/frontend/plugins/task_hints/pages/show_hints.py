import os
from collections import OrderedDict
from .constants import use_minified

_TASK_HINTS_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')


def show_hints(course, task, template_helper):
    """
        This is the method to display the hints options in the task menu
        and modal, to show all the task hints to the student.
    """

    add_static_files(template_helper)
    hints_basic_data = get_task_hints_basic_data(task)

    content = template_helper.get_custom_renderer(_TASK_HINTS_TEMPLATES_PATH, layout=False).hints_view(course, task,
                                                                                                       hints_basic_data)

    return str(content)


def get_task_hints_basic_data(task):
    """
        This is a method to get the title and penalty for each hint
        (Basic information to show on locked/unlocked hints)
    """
    all_hints = task._data.get('task_hints', {})

    all_hints_basic_data = OrderedDict([(index, {
        "penalty": hint["penalty"],
        "title": hint["title"],
        "id": hint["id"]
    }) for index, hint in all_hints.items()])

    return all_hints_basic_data


def get_user_total_penalty(taskid, username, database):
    """
    This is a method called by the `show_hints` hook to get the total penalty from
    the `user_hints` collection in database. This value is later used to calculate the student grade
    when a submission is sent.

    :param taskid: ID of the task
    :param username: Username of the student that made the submission
    :param database: General database object to find unlocked user hints in 'user_hints' collection
    :return: 'penalty' to be applied on the final grade of the submission
    """
    penalty = 0.0
    if username and taskid:
        data = database.user_hints.find_one({"taskid": taskid, "username": username})
        if data:
            penalty = data["total_penalty"]

    return penalty


def add_static_files(template_helper):
    if use_minified():
        template_helper.add_javascript("/task_hints/static/js/show_hints.min.js")
        template_helper.add_css("/task_hints/static/css/show_hints.min.css")
    else:
        template_helper.add_javascript("/task_hints/static/js/show_hints.js")
        template_helper.add_css("/task_hints/static/css/show_hints.css")
