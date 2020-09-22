import web
import tarfile

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from ..plagiarism_manager import PlagiarismManager


class CoursePlagiarismJobSummary(INGIniousAdminPage):
    """ Get the summary of a plagiarism job """

    @property
    def plagiarism_manager(self) -> PlagiarismManager:
        """ Returns the plugin manager singleton """
        return self.app.plagiarism_manager

    def GET_AUTH(self, courseid, bid):  # pylint: disable=arguments-differ
        """ GET request """

        course, _ = self.get_course_and_check_rights(courseid)
        plagiarism_check = self.plagiarism_manager.get_plagiarism_job_status(bid)

        if plagiarism_check is None:
            raise web.notfound()

        done = False
        submitted_on = plagiarism_check["submitted_on"]
        task_name = plagiarism_check["container_name"]
        container_title = task_name
        container_description = ""

        file_list = None
        retval = 0
        stdout = ""
        stderr = ""

        if "result" in plagiarism_check:
            done = True
            retval = plagiarism_check["result"]["retval"]
            stdout = plagiarism_check["result"].get("stdout", "")
            stderr = plagiarism_check["result"].get("stderr", "")

            if "file" in plagiarism_check["result"]:
                f = self.gridfs.get(plagiarism_check["result"]["file"])
                try:
                    tar = tarfile.open(fileobj=f, mode='r:gz')
                    file_list = set(tar.getnames()) - {''}
                    tar.close()
                except:
                    pass
                finally:
                    f.close()
        file_list = list(file_list)
        file_list.sort()
        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism/pages/templates')
        language = self.user_manager.session_language()
        return renderer.plagiarism_summary(course, bid, done, task_name, container_title,
                                           container_description, submitted_on, retval, stdout, stderr, file_list,
                                           language)
