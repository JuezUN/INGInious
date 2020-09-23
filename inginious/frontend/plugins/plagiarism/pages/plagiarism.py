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
        for entry in list(self.plagiarism_manager.get_all_plagiarism_checks_for_course(course_id)):
            check = {
                "task_name": entry["container_name"],
                "id": str(entry["_id"]),
                "submitted_on": entry["submitted_on"],
                "language": AVAILABLE_PLAGIARISM_LANGUAGES[entry['language']] if 'language' in entry else "Unknown",
                "status": "ok" if entry["result"]["retval"] == 0 else "ko"
            }

            plagiarism_checks.append(check)
        plagiarism_checks = sorted(plagiarism_checks, key=(lambda o: o["submitted_on"]), reverse=True)

        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism/pages/templates')
        language = self.user_manager.session_language()

        return renderer.plagiarism(course, plagiarism_checks, language)
