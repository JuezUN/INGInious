import os
from collections import OrderedDict
from inginious.frontend.parsable_text import ParsableText

_SHOW_HINTS_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__),'templates')

def show_hints(course, task, template_helper):

    add_static_files(template_helper)

    course_id = course.get_id()
    task_id = task.get_id()

    basic_hints_data = get_task_hints_basic_data(task)

    content = template_helper.get_custom_renderer(_SHOW_HINTS_TEMPLATES_PATH, layout=False).hints_view(course_id, task_id, basic_hints_data)

    return str(content)

def get_task_hints_basic_data(task):
    """ This is a method to get the title and penalty for each hint
        (Basic information to show on locked/unlocked hints)
    """
    all_hints = task._data.get('task_hints',[])

    all_hints_basic_data = OrderedDict([(index, {
            "penalty" : hint["penalty"],
            "title" : hint["title"]
        }) for index, hint in all_hints.items()])

    return all_hints_basic_data

def add_static_files(template_helper):

    template_helper.add_javascript("/show_hints/static/show_hints.js")
