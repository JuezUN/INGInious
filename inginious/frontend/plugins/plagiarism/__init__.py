# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import tarfile
import mimetypes
import urllib.request, urllib.parse, urllib.error
import tempfile
import web
import os

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.utils import create_static_resource_page
from .plagiarism_manager import PlagiarismManager
from .pages.plagiarism import PlagiarismPage
from .pages.plagiarism_create import PlagiarismCreate
from .pages.plagiarism_summary import CoursePlagiarismJobSummary

_STATIC_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "static")


class CourseBatchJobDownload(INGIniousAdminPage):
    """ Get the file of a batch job """

    @property
    def batch_manager(self) -> PlagiarismManager:
        """ Returns the plugin manager singleton """
        return self.app.plagiarism_manager

    def GET_AUTH(self, courseid, bid, path=""):  # pylint: disable=arguments-differ
        """ GET request """

        self.get_course_and_check_rights(courseid)  # simply verify rights
        batch_job = self.batch_manager.get_plagiarism_job_status(bid)

        if batch_job is None:
            raise web.notfound()

        if "result" not in batch_job or "file" not in batch_job["result"]:
            raise web.notfound()

        f = self.gridfs.get(batch_job["result"]["file"])

        # hack for index.html:
        if path == "/":
            path = "/index.html"

        if path == "":
            web.header('Content-Type', 'application/x-gzip', unique=True)
            web.header('Content-Disposition', 'attachment; filename="' + bid + '.tar.gz"', unique=True)
            return f.read()
        else:
            path = path[1:]  # remove the first /
            if path.endswith('/'):  # remove the last / if it exists
                path = path[0:-1]

            try:
                tar = tarfile.open(fileobj=f, mode='r:gz')
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


def add_admin_menu(course):  # pylint: disable=unused-argument
    """ Add a menu for the plagiarism checker in the administration """
    return "plagiarism", "<i class='fa fa-check-circle-o fa-fw'></i>&nbsp; Plagiarism"


def init(plugin_manager, _, client, conf):
    """
        Init the plugin.
        Available configuration in configuration.yaml:
        ::

            - plugin_module: "inginious.frontend.plugins.plagiarism"
            - storage_path: 'path/to/storage/results'
    """
    plugin_manager.add_page(r'/plagiarism/static/(.*)', create_static_resource_page(_STATIC_FOLDER_PATH))

    # TODO: Rather than adding to the app, create a singleton like code_preview?
    plugin_manager._app.plagiarism_manager = PlagiarismManager(client, plugin_manager.get_database(),
                                                               plugin_manager._app.gridfs,
                                                               plugin_manager.get_submission_manager(),
                                                               plugin_manager.get_user_manager(),
                                                               plugin_manager._app.task_factory._filesystem.prefix)

    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism', PlagiarismPage)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/create', PlagiarismCreate)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/summary/([^/]+)', CoursePlagiarismJobSummary)
    # plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/grouped_summary/([^/]+)', GroupedListPage)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/download/([^/]+)', CourseBatchJobDownload)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/download/([^/]+)(/.*)', CourseBatchJobDownload)

    plugin_manager.add_hook("css", lambda: "/plagiarism/static/css/plagiarism.css")

    plugin_manager.add_hook('course_admin_menu', add_admin_menu)
