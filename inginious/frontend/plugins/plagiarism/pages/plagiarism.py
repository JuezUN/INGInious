import web

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from ..plagiarism_manager import PlagiarismManagerSingleton
from ..constants import AVAILABLE_PLAGIARISM_LANGUAGES


class PlagiarismPage(INGIniousAdminPage):
    """ Plagiarism page """

    @property
    def plagiarism_manager(self) -> PlagiarismManagerSingleton:
        """ Returns the plagiarism manager singleton """
        return PlagiarismManagerSingleton.get_instance()

    def GET_AUTH(self, course_id):  # pylint: disable=arguments-differ
        """ GET request """

        course, _ = self.get_course_and_check_rights(course_id)

        web_input = web.input()
        if "drop" in web_input:
            try:
                self.plagiarism_manager.drop_plagiarism_check(web_input["drop"])
            except:
                pass

        plagiarism_checks = []
        for plagiarism_check in list(self.plagiarism_manager.get_all_plagiarism_checks_for_course(course_id)):
            # TODO: 'container_name' is deprecated, when 'batch_jobs' collection is not longer used, update the code.
            if 'result' not in plagiarism_check:
                status = 'waiting'
            elif plagiarism_check["result"]["retval"] == 0:
                status = "ok"
            else:
                status = 'ko'
            check = {
                "task_name": plagiarism_check["container_name"] if 'container_name' in plagiarism_check else
                plagiarism_check["task_name"],
                "id": str(plagiarism_check["_id"]),
                "submitted_on": plagiarism_check["submitted_on"],
                "language": AVAILABLE_PLAGIARISM_LANGUAGES[
                    plagiarism_check['language']] if 'language' in plagiarism_check else "Unknown",
                "status": status
            }

            plagiarism_checks.append(check)
        plagiarism_checks = sorted(plagiarism_checks, key=(lambda o: o["submitted_on"]), reverse=True)

        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism/pages/templates')
        language = self.user_manager.session_language()

        return renderer.plagiarism(course, plagiarism_checks, language)
