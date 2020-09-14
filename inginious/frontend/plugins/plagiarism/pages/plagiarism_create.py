import web
import hashlib
from datetime import datetime
from collections import OrderedDict

from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from ..plagiarism_manager import PlagiarismManager


class PlagiarismCreate(INGIniousAdminPage):
    """ Creates new plagiarism checks """

    @property
    def plagiarism_manager(self) -> PlagiarismManager:
        """ Returns the batch manager singleton """
        return self.app.plagiarism_manager

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, container_title, container_description, container_args = self.get_basic_info(
            courseid)
        return self.page(course, container_title, container_description, container_args)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, container_title, container_description, container_args = self.get_basic_info(
            courseid)
        errors = []
        has_errors = False

        data = web.input()
        if 'task' not in data or 'language' not in data:
            errors.append("Please fill all the fields.")
            has_errors = True
        elif data['task'] == '' or data['language'] == '':
            errors.append("Please fill all the fields.")
            has_errors = True
        if data['language'] not in container_args['language']['choices']:
            errors.append("Language is not valid")
            has_errors = True

        if not has_errors:
            data["real_title"] = self.task_factory.get_task(course, data["task"]).get_name(
                self.user_manager.session_language())
            self.plagiarism_manager.add_plagiarism_check(course, data, self.user_manager.session_username())

        if not has_errors:
            raise web.seeother('/admin/{}/plagiarism'.format(courseid))
        else:
            return self.page(course, container_title, container_description, container_args, errors)

    def get_basic_info(self, courseid):
        course, _ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        container_title = "JPlag"
        container_description = ParsableText("Plagiarism tool".encode('utf-8').decode("unicode_escape"), 'rst')

        container_args = OrderedDict({
            "task": OrderedDict({
                "type": "text",
                "name": "Task to check",
                "path": "task.txt",
                "description": "Task you want to check."
            }),
            "language": OrderedDict({
                "type": "text",
                "name": "Language",
                "path": "lang.txt",
                "choices": ['python3', 'java17', 'java11', 'c/c++', 'text'],
                "description": "Language used in the submissions."
            }),
        })

        for val in container_args.values():
            if "description" in val:
                val['description'] = ParsableText(val['description'].encode('utf-8').decode("unicode_escape"),
                                                  'rst').parse()

        return course, container_title, container_description, container_args

    def page(self, course, container_title, container_description, container_args, error=None,
             container_name="JPlag"):

        if "submissions" in container_args and container_args["submissions"]["type"] == "file":
            del container_args["submissions"]
        if "course" in container_args and container_args["course"]["type"] == "file":
            del container_args["course"]
        tasks = [self.task_factory.get_task(course, x) for x in course.get_tasks()]

        # self.template_helper.add_javascript(web.ctx.homepath + '/static/webapp/js/selectize.min.js', "header")
        # self.template_helper.add_css(web.ctx.homepath + '/static/webapp/css/selectize.bootstrap3.css')
        # self.template_helper.add_javascript(web.ctx.homepath + '/static/webapp/js/HoldOn.min.js', "header")
        # self.template_helper.add_css(web.ctx.homepath + '/static/webapp/css/HoldOn.min.css')
        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism/pages/templates')
        language = self.user_manager.session_language()
        return renderer.plagiarism_create(course, container_name, container_title, container_description,
                                          container_args, tasks, error, language)
