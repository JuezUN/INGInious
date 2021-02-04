import os

from inginious.frontend.plugins.multilang.problems.languages import get_all_available_languages
from inginious.frontend.parsable_text import ParsableText

_TASK_EDITORIAL_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")

def is_task_open(task):

    return task.get_accessible_time().is_open()

def editorial_task_tab(course, taskid, task_data, template_helper):

    tab_id = 'tab_editorial'
    link = '<i class="fa fa-graduation-cap fa-fw"></i>&nbsp; ' + _("Task editorial")

    task_environment = task_data.get('environment')
    task_solution_code_language = task_data.get('solution_code_language')

    content = template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH, layout=False).task_editorial(task_data, task_environment, get_all_available_languages(), task_solution_code_language)
    return tab_id, link ,content

def editorial_task_preview(course, task, template_helper):

    task_tutorial_description_content = task._data.get('tutorial_description')
    task_solution_code = task._data.get('solution_code')
    task_solution_code_language = task._data.get('solution_code_language')

    if task_tutorial_description_content is not None:
        task_tutorial_description = ParsableText(task_tutorial_description_content, 'rst')
    else:
        task_tutorial_description = None

    content = template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH, layout=False).task_editorial_preview(course, task, is_task_open(task), get_all_available_languages(), task_tutorial_description, task_solution_code, task_solution_code_language)
    return str(content)

def check_editorial_submit(course, taskid, task_data, task_fs):

    #Delete empty fields to show tutorial and solution in preview

    if task_data['tutorial_description'] is '':
        del  task_data['tutorial_description']

    if task_data['solution_code'] is '':
        del task_data['solution_code']
        del task_data['solution_code_language']
    else:
        if task_data['solution_code_language'] is '0':
            del task_data['solution_code_language']
