import web

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from ..plagiarism_manager import PlagiarismManagerSingleton
from ..constants import AVAILABLE_PLAGIARISM_LANGUAGES, ALLOWED_ENVIRONMENTS


class PlagiarismCreate(INGIniousAdminPage):
    """ Creates new plagiarism checks """

    @property
    def plagiarism_manager(self) -> PlagiarismManagerSingleton:
        """ Returns the batch manager singleton """
        return PlagiarismManagerSingleton.get_instance()

    def GET_AUTH(self, course_id):  # pylint: disable=arguments-differ
        """ GET request """
        course, _ = self.get_course_and_check_rights(course_id, allow_all_staff=False)
        return self.page(course)

    def POST_AUTH(self, course_id):  # pylint: disable=arguments-differ
        """ POST request """
        course, __ = self.get_course_and_check_rights(course_id, allow_all_staff=False)
        errors = []
        has_errors = False

        data = web.input()

        if 'taskid' not in data or 'language' not in data:
            errors.append(_("Please fill all the fields."))
            has_errors = True
        elif data['taskid'] == '' or data['language'] == '':
            errors.append(_("Please fill all the fields."))
            has_errors = True
        if data['language'] not in AVAILABLE_PLAGIARISM_LANGUAGES:
            errors.append(_("Language is not valid"))
            has_errors = True
        if 'base_code' not in data:
            errors.append(_("Base code is not present."))
            has_errors = True

        data['base_code'] = data['base_code'].decode("utf-8")
        task = self.task_factory.get_task(course, data["taskid"])
        if task.get_environment() not in ALLOWED_ENVIRONMENTS:
            errors.append(_("Task environment is not allowed to generate a plagiarism check."))
            has_errors = True

        if not has_errors:
            data['task'] = task
            plagiarism_has_error, error = self.plagiarism_manager.add_plagiarism_check(course, data)
            if plagiarism_has_error:
                errors.append(error)
                has_errors = True

        if not has_errors:
            raise web.seeother('/admin/{}/plagiarism'.format(course_id))
        else:
            return self.page(course, errors)

    def page(self, course, error=None):
        tasks = sorted([self.task_factory.get_task(course, task) for task in course.get_tasks() if
                        self.task_factory.get_task(course, task).get_environment() in ALLOWED_ENVIRONMENTS],
                       key=lambda task: task.get_name(self.user_manager.session_language()))

        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism/pages/templates')
        language = self.user_manager.session_language()
        return renderer.plagiarism_create(course, AVAILABLE_PLAGIARISM_LANGUAGES, tasks, error, language)
