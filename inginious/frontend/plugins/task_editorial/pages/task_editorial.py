import os

from inginious.frontend.plugins.multilang.problems.languages import get_all_available_languages
from inginious.frontend.pages.course_admin.task_edit import CourseEditTask

_TASK_EDITORIAL_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")

def check_task_access(task):

    return task.get_accessible_time().is_open()

def editorial_task_tab(course, taskid, task_data, template_helper):

    tab_id = 'tab_editorial'
    link = '<i class="fa fa-graduation-cap fa-fw"></i>&nbsp; ' + _('Task editorial')

    task = course.get_task(taskid)
    task_environment = task.get_environment();

    content = template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH, layout=False).task_editorial(task_data, task, get_all_available_languages(), task_environment)
    return tab_id, link ,content

def editorial_task_preview(course, task, template_helper):

    if(check_task_access(task)):
        return
    else:
        content = template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH, layout=False).task_editorial_preview(course, task, get_all_available_languages())
        return str(content)

def check_editorial_submit(course, taskid, task_data, task_fs):

    task_data['solution_code_language'] = CourseEditTask.dict_from_prefix('solution_code_language',task_data)

    all_languages = get_all_available_languages()

    if not (task_data['solution_code_language'] in all_languages):
        del task_data['solution_code_language']
