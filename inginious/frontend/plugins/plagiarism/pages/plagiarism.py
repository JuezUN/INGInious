import web

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from ..plagiarism_manager import PlagiarismManager


class PlagiarismPage(INGIniousAdminPage):
    """ Plagiarism page """

    @property
    def plagiarism_manager(self) -> PlagiarismManager:
        """ Returns the plagiarism manager singleton """
        return self.app.plagiarism_manager

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """

        course, _ = self.get_course_and_check_rights(courseid)

        web_input = web.input()
        if "drop" in web_input:
            try:
                self.plagiarism_manager.drop_batch_job(web_input["drop"])
            except:
                pass

        plagiarism_checks = []
        for entry in list(self.plagiarism_manager.get_all_batch_jobs_for_course(courseid)):
            ne = {"container_name": entry["container_name"],
                  "bid": str(entry["_id"]),
                  "submitted_on": entry["submitted_on"]}
            if "result" in entry:
                ne["status"] = "ok" if entry["result"]["retval"] == 0 else "ko"
            else:
                ne["status"] = "waiting"
            plagiarism_checks.append(ne)
        plagiarism_checks = sorted(plagiarism_checks, key=(lambda o: o["submitted_on"]), reverse=True)

        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism/pages/templates')
        language = self.user_manager.session_language()
        return renderer.plagiarism(course, plagiarism_checks, language)
