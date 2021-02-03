import os

from inginious.frontend.plugins.multilang.problems.languages import get_all_available_languages
from inginious.frontend.pages.course_admin.task_edit import CourseEditTask
from inginious.frontend.parsable_text import ParsableText

_TASK_EDITORIAL_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")

def is_task_open(task):

    return task.get_accessible_time().is_open()

def editorial_task_tab(course, taskid, task_data, template_helper):

    tab_id = 'tab_editorial'
    link = '<i class="fa fa-graduation-cap fa-fw"></i>&nbsp; ' + _("Task editorial")

    task_environment = task_data.get('environment')
    task_solution_code_language = task_data.get('solution_code_language')

    if task_environment in {"multiple_languages" , "Data Science" , "HDL"} or task_environment is None:

        content = template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH, layout=False).task_editorial(task_data, get_all_available_languages(), task_solution_code_language)
        return tab_id, link ,content
    else:
        return

def editorial_task_preview(course, task, template_helper):

    if is_task_open(task):
        return
    else:

        task_tutorial_description_content = task._data.get('tutorial_description')
        task_solution_code = task._data.get('solution_code')
        task_solution_code_language = task._data.get('solution_code_language')

        task_tutorial_description = ParsableText(task_tutorial_description_content, 'rst')

        content = template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH, layout=False).task_editorial_preview(course, task, get_all_available_languages(), task_tutorial_description, task_solution_code, task_solution_code_language)
        return str(content)

def check_editorial_submit(course, taskid, task_data, task_fs):

    task_data['solution_code_language'] = CourseEditTask.dict_from_prefix('solution_code_language',task_data)

    all_languages = get_all_available_languages()

    if not (task_data['solution_code_language'] in all_languages):
        del task_data['solution_code_language']
