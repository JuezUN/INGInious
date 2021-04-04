import os

from inginious.frontend.pages.course_admin.task_edit import CourseEditTask
from inginious.frontend.parsable_text import ParsableText

_SHOW_HINTS_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__),'templates')

def show_hints(course, task, template_helper):

    add_static_files(template_helper)

    course_id = course.get_id()
    task_id = task.get_id()

    content = template_helper.get_custom_renderer(_SHOW_HINTS_TEMPLATES_PATH, layout=False).hints_view(course_id, task_id)

    return str(content)

def add_static_files(template_helper):

    template_helper.add_javascript("/show_hints/static/show_hints.js")
