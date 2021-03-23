import os

from inginious.frontend.pages.course_admin.task_edit import CourseEditTask

_SHOW_HINTS_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__),'templates')

def show_hints(course, task, template_helper):

    add_static_files(template_helper)

    task_hints = task._data.get('task_hints', {})

    content = template_helper.get_custom_renderer(_SHOW_HINTS_TEMPLATES_PATH, layout=False).hints_view(task_hints)

    return str(content)

def add_static_files(template_helper):

    template_helper.add_javascript("/task_editorial/static/show_hints.js")
