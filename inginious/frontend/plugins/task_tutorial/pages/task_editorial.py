import os
import json

from collections import OrderedDict
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage

_TASK_EDITORIAL_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")

def editorial_task_tab(course, taskid, task_data, template_helper):

    tab_id = 'tab_editorial'
    link = '<i class="fa fa-graduation-cap fa-fw"></i>&nbsp; ' + _('Task editorial')
    content = template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH, layout=False).task_editorial(task_data, taskid)
    return tab_id, link ,content

class EditorialCourseAdminPage(INGIniousAdminPage):

    def GET_AUTH(self, course_id):

        course, _ = self.get_course_and_check_rights(course_id)

        return self.get_course_tasks(course)

    def get_course_tasks(self, course):

        tasks = self.task_factory.get_readable_tasks(course)
        tasks_list = OrderedDict()
        for task in tasks:
            tasks_list[task] = {"name": course.get_task(task).get_name(self.user_manager.session_language())}
        page = self.template_helper.get_custom_renderer(_TASK_EDITORIAL_TEMPLATE_PATH).course_admin_editorial(course, tasks_list)
        return page

def editorial_course_admin_menu(course):

    #content = template_helper.get_custom_renderer(_TASK_TUTORIAL_TEMPLATE_PATH, layout=False).course_admin_tutorials(3)
    return "editorial", '<i class="fa fa-graduation-cap" aria-hidden="true"></i> {}'.format("Course editorials")
