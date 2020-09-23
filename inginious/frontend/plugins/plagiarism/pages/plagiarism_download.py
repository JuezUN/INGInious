import tarfile
import mimetypes
import urllib.request
import tempfile
import web

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from ..plagiarism_manager import PlagiarismManagerSingleton


class PlagiarismDownload(INGIniousAdminPage):
    """ Get the file of a batch job """

    @property
    def batch_manager(self) -> PlagiarismManagerSingleton:
        """ Returns the plugin manager singleton """
        return PlagiarismManagerSingleton.get_instance()

    def GET_AUTH(self, course_id, check_id, path=""):  # pylint: disable=arguments-differ
        """ GET request """

        self.get_course_and_check_rights(course_id)  # simply verify rights
        plagiarism_check = self.batch_manager.get_plagiarism_check(check_id)

        if plagiarism_check is None:
            raise web.notfound()

        if "result" not in plagiarism_check or "file" not in plagiarism_check["result"]:
            raise web.notfound()

        results_file = self.gridfs.get(plagiarism_check["result"]["file"])

        # hack for index.html:
        if path == "/":
            path = "/index.html"

        if path == "":
            web.header('Content-Type', 'application/x-gzip', unique=True)
            web.header('Content-Disposition', 'attachment; filename="' + check_id + '.tar.gz"', unique=True)
            return results_file.read()
        else:
            path = path[1:]  # remove the first /
            if path.endswith('/'):  # remove the last / if it exists
                path = path[0:-1]

            try:
                tar = tarfile.open(fileobj=results_file, mode='r:gz')
                file_info = tar.getmember(path)
            except:
                raise web.notfound()

            if file_info.isdir():  # tar.gz the dir and return it
                tmp = tempfile.TemporaryFile()
                new_tar = tarfile.open(fileobj=tmp, mode='w:gz')
                for m in tar.getmembers():
                    new_tar.addfile(m, tar.extractfile(m))
                new_tar.close()
                tmp.seek(0)
                return tmp
            elif not file_info.isfile():
                raise web.notfound()
            else:  # guess a mime type and send it to the browser
                to_dl = tar.extractfile(path).read()
                mimetypes.init()
                mime_type = mimetypes.guess_type(urllib.request.pathname2url(path))
                web.header('Content-Type', mime_type[0])
                return to_dl
