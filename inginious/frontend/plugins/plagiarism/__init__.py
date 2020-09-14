# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import tarfile
import mimetypes
import urllib.request, urllib.parse, urllib.error
import tempfile
import web

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from .plagiarism_manager import PlagiarismManager
from .pages.plagiarism import PlagiarismPage
from .pages.plagiarism_create import PlagiarismCreate


class GroupedListPage(INGIniousAdminPage):
    """ Batch operation management """

    @property
    def batch_manager(self) -> PlagiarismManager:
        """ Returns the batch manager singleton """
        return self.app.plagiarism_manager

    def GET_AUTH(self, courseid, hash):  # pylint: disable=arguments-differ
        """ GET request """

        course, _ = self.get_course_and_check_rights(courseid)

        web_input = web.input()
        if "drop" in web_input:  # delete an old batch job
            try:
                self.batch_manager.drop_batch_job(web_input["drop"])
            except:
                pass

        operations = []
        for entry in list(self.batch_manager.get_all_grouped_batch_jobs_for_course_and_hash(courseid, hash)):
            ne = {"container_name": entry["container_name"],
                  "bid": str(entry["_id"]),
                  "submitted_on": entry["submitted_on"]}
            if "result" in entry:
                ne["status"] = "ok" if entry["result"]["retval"] == 0 else "ko"
            else:
                ne["status"] = "waiting"
            operations.append(ne)
        operations = sorted(operations, key=(lambda o: o["submitted_on"]), reverse=True)

        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism')
        return renderer.grouped_batch(course, operations)


class CourseBatchJobDownload(INGIniousAdminPage):
    """ Get the file of a batch job """

    @property
    def batch_manager(self) -> PlagiarismManager:
        """ Returns the plugin manager singleton """
        return self.app.plagiarism_manager

    def GET_AUTH(self, courseid, bid, path=""):  # pylint: disable=arguments-differ
        """ GET request """

        self.get_course_and_check_rights(courseid)  # simply verify rights
        batch_job = self.batch_manager.get_batch_job_status(bid)

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


class CourseBatchJobSummary(INGIniousAdminPage):
    """ Get the summary of a batch job """

    @property
    def batch_manager(self) -> PlagiarismManager:
        """ Returns the plugin manager singleton """
        return self.app.plagiarism_manager

    def GET_AUTH(self, courseid, bid):  # pylint: disable=arguments-differ
        """ GET request """

        course, _ = self.get_course_and_check_rights(courseid)
        batch_job = self.batch_manager.get_batch_job_status(bid)

        if batch_job is None:
            raise web.notfound()

        done = False
        submitted_on = batch_job["submitted_on"]
        container_name = batch_job["container_name"]
        container_title = container_name
        container_description = ""

        file_list = None
        retval = 0
        stdout = ""
        stderr = ""

        try:
            container_metadata = self.batch_manager.get_batch_container_metadata(container_name)
            if container_metadata == (None, None, None):
                container_title = container_metadata[0]
                container_description = container_metadata[1]
        except:
            pass

        if "result" in batch_job:
            done = True
            retval = batch_job["result"]["retval"]
            stdout = batch_job["result"].get("stdout", "")
            stderr = batch_job["result"].get("stderr", "")

            if "file" in batch_job["result"]:
                f = self.gridfs.get(batch_job["result"]["file"])
                try:
                    tar = tarfile.open(fileobj=f, mode='r:gz')
                    file_list = set(tar.getnames()) - set([''])
                    tar.close()
                except:
                    pass
                finally:
                    f.close()
        file_list = list(file_list)
        file_list.sort()
        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism')
        language = self.user_manager.session_language()
        return renderer.batch_summary(course, bid, done, container_name, container_title,
                                      container_description, submitted_on, retval, stdout, stderr, file_list, language)


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
    # page_pattern_course =  r'/admin/([^/]+)/plagiarism'
    plugin_manager._app.plagiarism_manager = PlagiarismManager(client, plugin_manager.get_database(),
                                                               plugin_manager._app.gridfs,
                                                               plugin_manager.get_submission_manager(),
                                                               plugin_manager.get_user_manager(),
                                                               plugin_manager._app.task_factory._filesystem.prefix)

    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism', PlagiarismPage)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/create', PlagiarismCreate)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/summary/([^/]+)', CourseBatchJobSummary)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/grouped_summary/([^/]+)', GroupedListPage)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/download/([^/]+)', CourseBatchJobDownload)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/download/([^/]+)(/.*)', CourseBatchJobDownload)

    plugin_manager.add_hook('course_admin_menu', add_admin_menu)
