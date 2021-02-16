import os

from inginious.frontend.plugins.multilang.problems.languages import get_all_available_languages
from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.pages.course_admin.task_edit import CourseTaskFiles

_TASK_EDITORIAL_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")


def is_task_open(task):
    return task.get_accessible_time().is_open()


def editorial_task_tab(course, taskid, task_data, template_helper):
    tab_id = 'tab_editorial'
    link = '<i class="fa fa-graduation-cap fa-fw"></i>&nbsp; ' + _("Task editorial")

    content = template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH, layout=False).task_editorial(task_data)
    return tab_id, link, content


def editorial_task_preview(course, task, template_helper):
    task_tutorial_description_content = task._data.get('tutorial_description')
    task_solution_code = task._data.get('solution_code')
    task_solution_code_language = task._data.get('solution_code_language')
    task_solution_code_notebook = task._data.get('solution_code_notebook')
    task_environment = task._data.get('environment')

    if task_tutorial_description_content is not None:
        task_tutorial_description = ParsableText(task_tutorial_description_content, 'rst')
    else:
        task_tutorial_description = None

    task_problems = task.get_problems()
    if task_environment in {"multiple_languages", "Data Science", "HDL"} and task_problems[0].get_type() in {"code_multiple_languages", "code_file_multiple_languages"}:
        if task_solution_code_language and task_solution_code_language not in task_problems[0].get_original_content()['languages'].values():
            task_solution_code_language = None

    content = template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH, layout=False).task_editorial_preview(
        course, task, is_task_open(task), get_all_available_languages(), task_tutorial_description, task_solution_code,
        task_solution_code_language, task_solution_code_notebook, task_environment)
    return str(content)


def check_editorial_submit(course, taskid, task_data, task_fs):
    if task_data['tutorial_description'] is '':
        del task_data['tutorial_description']

    if task_data['environment'] in {"multiple_languages", "Data Science", "HDL"}:

        # Delete empty fields to show tutorial and solution in preview
        if task_data['solution_code'] is '':
            del task_data['solution_code']
            del task_data['solution_code_language']
        else:
            if task_data['solution_code_language'] is '0':
                del task_data['solution_code_language']

    elif task_data['environment'] in {"Notebook"}:

        all_files = CourseTaskFiles.get_task_filelist(course._task_factory, course.get_id(), taskid)
        all_files = {complete_name[1:] if complete_name.startswith("/") else complete_name for
                     level, is_directory, name, complete_name in all_files}

        if task_data['solution_code_notebook'] is '0' or not task_data['solution_code_notebook'] in all_files:
            del task_data['solution_code_notebook']
