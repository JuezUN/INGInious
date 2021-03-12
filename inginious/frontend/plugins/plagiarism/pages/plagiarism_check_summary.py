import web
import tarfile

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from ..plagiarism_manager import PlagiarismManagerSingleton
from ..constants import AVAILABLE_PLAGIARISM_LANGUAGES, add_static_files


class PlagiarismCheckSummary(INGIniousAdminPage):
    """ Get the summary of a plagiarism check """

    @property
    def plagiarism_manager(self) -> PlagiarismManagerSingleton:
        """ Returns the plugin manager singleton """
        return PlagiarismManagerSingleton.get_instance()

    def GET_AUTH(self, course_id, check_id):  # pylint: disable=arguments-differ
        """ GET request """

        course, _ = self.get_course_and_check_rights(course_id)
        plagiarism_check = self.plagiarism_manager.get_plagiarism_check(check_id)

        if plagiarism_check is None:
            raise web.notfound()

        done = False
        created_on = plagiarism_check["submitted_on"]
        # TODO: 'container_name' is deprecated, when 'batch_jobs' collection is not longer used, update the code.
        task_name = plagiarism_check["container_name"] if 'container_name' in plagiarism_check else plagiarism_check[
            "task_name"]
        language = AVAILABLE_PLAGIARISM_LANGUAGES[
            plagiarism_check['language']] if 'language' in plagiarism_check else "Unknown"
        file_list = []
        return_code = 0
        stdout = ""
        stderr = ""

        if "result" in plagiarism_check:
            done = True
            return_code = plagiarism_check["result"]["retval"]
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

        add_static_files(self.template_helper)
        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism/pages/templates')
        return renderer.plagiarism_check_summary(course, check_id, done, task_name, created_on, return_code, stdout,
                                                 stderr, file_list, language)
