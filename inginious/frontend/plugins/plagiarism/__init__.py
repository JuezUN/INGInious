# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
import hashlib
import tarfile
import mimetypes
import urllib.request, urllib.parse, urllib.error
import tempfile
import copy
import web
from datetime import datetime

from inginious.frontend.accessible_time import AccessibleTime
from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.plagiarism.batch_manager import BatchManager
from inginious.frontend.plugins.plagiarism.contest_manager import ContestManager


class PlagiarismPage(INGIniousAdminPage):
    """ Plagiarism checker """

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, _ = self.get_course_and_check_rights(courseid, allow_all_staff=False)
        return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, _ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        errors = []

        new_data = {}
        try:
            data = web.input()
            new_data['name'] = data['name']
            new_data['lang'] = data.get('lang','c/c++')

        except:
            errors.append('User returned an invalid form.')

        if len(errors) == 0:
            errors = None
            course, _ = self.get_course_and_check_rights(courseid, allow_all_staff=False)  # don't forget to reload the modified course

        return self.page(course, errors, errors is None)

    def page(self, course, errors=None, saved=False):
        """ Get all data and display the page """
        self.template_helper.add_javascript(web.ctx.homepath + '/static/webapp/js/selectize.min.js', "header")
        self.template_helper.add_css(web.ctx.homepath + '/static/webapp/css/selectize.bootstrap3.css')
        self.template_helper.add_javascript(web.ctx.homepath + '/static/webapp/js/pace.min.js', "header")
        self.template_helper.add_css(web.ctx.homepath + '/static/webapp/css/pace-theme-center-radar.css')
        problems = [self.task_factory.get_task(course, x) for x in
                    course.get_tasks()]
        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism')
        language = self.user_manager.session_language()
        return renderer.plagiarism(course, problems, errors, saved, language)


class CourseBatchOperations(INGIniousAdminPage):
    """ Batch operation management """

    @property
    def batch_manager(self) -> BatchManager:
        """ Returns the batch manager singleton """
        return self.app.batch_manager

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """

        course, _ = self.get_course_and_check_rights(courseid)

        web_input = web.input()
        if "drop" in web_input:  # delete an old batch job
            try:
                self.batch_manager.drop_batch_job(web_input["drop"])
            except:
                pass

        if "grouped_drop" in web_input:  # delete an old batch job
            try:
                self.batch_manager.drop_grouped_batch_job(web_input["grouped_drop"])
            except Exception as e:
                pass

        operations = []
        for entry in list(self.batch_manager.get_all_batch_jobs_for_course(courseid)):
            ne = {"container_name": entry["container_name"],
                  "bid": str(entry["_id"]),
                  "submitted_on": entry["submitted_on"]}
            if "result" in entry:
                ne["status"] = "ok" if entry["result"]["retval"] == 0 else "ko"
            else:
                ne["status"] = "waiting"
            operations.append(ne)
        operations = sorted(operations, key=(lambda o: o["submitted_on"]), reverse=True)


        operations_grouped = []

        grouped_entries = self.batch_manager.get_all_grouped_batch_jobs_for_course(courseid)
        grouped_set_entries = list(
            (x.get("group_name", ""), x.get("group_hash", ''), x["submitted_on"]) for x in grouped_entries if
            x.get("group_name", "") != "")
        names = []
        grouped_entries = []
        for entry in grouped_set_entries:
            if entry[0] not in names:
                names.append(entry[0])
                grouped_entries.append(entry)

        for name,hash,subm in grouped_entries:
            ne = {"name": name,
                  "hash": hash,
                  "submitted_on":subm}
            operations_grouped.append(ne)
        operations_grouped = sorted(operations_grouped, key=(lambda o: o["submitted_on"]), reverse=True)
        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism')
        language = self.user_manager.session_language()
        return renderer.batch(course, operations, operations_grouped, language)


class GroupedListPage(INGIniousAdminPage):
    """ Batch operation management """

    @property
    def batch_manager(self) -> BatchManager:
        """ Returns the batch manager singleton """
        return self.app.batch_manager

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

class CourseBatchJobCreate(INGIniousAdminPage):
    """ Creates new batch jobs """
    def __init__(self):
        super().__init__()
        self.contest_manager = ContestManager(self.user_manager, self.database, self.course_factory, self.template_helper, 
        self.template_helper, None)

    @property
    def batch_manager(self) -> BatchManager:
        """ Returns the batch manager singleton """
        return self.app.batch_manager

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, container_title, container_description, container_args, container_contest_args = self.get_basic_info(courseid)
        return self.page(course, container_title, container_description, container_args, container_contest_args)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """        
        course, container_title, container_description, container_args, container_contest_args = self.get_basic_info(courseid)
        errors = []

        new_data = {}
        try:
            data = web.input()
            new_data['name'] = data['name']
            new_data['lang'] = data.get('lang','c/c++')
        except:
            print("Wrong")
        # Verify that we have the right keys
        try:
            container_all = container_args.copy()
            container_all.update(container_contest_args)
            file_args = {key: {} for key in container_all if key != "submissions" and key != "course" and container_all[key]["type"] == "file"}

            batch_input = web.input(**file_args)
            #web.debug(batch_input)
            is_single = "single_problem" in batch_input
            for key in container_all:
                if (key != "submissions" and key != "course") or container_all[key]["type"] != "file":
                    if container_all[key]["type"] == "file":
                        batch_input[key] = batch_input[key].file.read()
        except Exception as e:
            #web.debug(e)
            errors.append("Please fill all the fields.")

        if len(errors) == 0:
            #try:
            if "single_problem" in batch_input:
                batch_input["real_title"] = batch_input["task"] + " - " + self.task_factory.get_task(course, batch_input["task"]).get_name(self.user_manager.session_language())
                #web.debug(batch_input)
                #web.debug()
                self.batch_manager.add_batch_job(course, batch_input,
                                                 self.user_manager.session_username(),
                                                 self.user_manager.session_email())
            elif "tab_contest" in batch_input:
                contest_data = self.contest_manager.get_contest_data(course, batch_input["contest"])
                batch_input["group_name"] = contest_data["name"] + " - " + str(datetime.now())

                batch_input["group_hash"] = hashlib.md5(batch_input["group_name"].encode("utf-8")).hexdigest()
                # web.debug(batch_input)
                # web.debug()
                for problem in contest_data["content"]:
                    #web.debug(contest_data)
                    batch_input["task"] = problem
                    batch_input["real_title"] = contest_data["name"] + " - " + problem
                    self.batch_manager.add_batch_job(course, batch_input,
                                                 self.user_manager.session_username(),
                                                 self.user_manager.session_email())
            #except Exception as e:
                #web.debug(e)

                #errors.append("An error occurred while starting the job")

        if len(errors) == 0:
            raise web.seeother('/admin/{}/plagiarism'.format(courseid))
        else:
            return self.page(course, container_title, container_description, container_args, container_contest_args, errors)

    def get_basic_info(self, courseid):
        course, _ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        container_title = "JPlag"
        container_description = ParsableText("Plagiarism tool".encode('utf-8').decode("unicode_escape"), 'rst')

        container_args = {
            "task": {
                "type": "text",
                "name": "Problem to check",
                "path": "task.txt",
                "description": "Id of the problem you want to check."
            },
            "language": {
                "type": "text",
                "name": "Language",
                "path": "lang.txt",
                "choices": ['python3', 'java17', 'java15', 'java15dm', 'java12', 'java11', 'c/c++', 'c#-1.2', 'char',
                            'text', 'scheme'],
                "description": "Language used in the submissions."
            },
        }

        container_contest_args = container_args.copy()

        container_contest_args["contest"] = {
            "type": "text",
            "name": "Contests",
            "description": "The contest you want to check",
            "choices": {x:y["name"] for x,y in self.contest_manager.get_all_contest_data(course).items()}
        }

        del container_contest_args["task"]

        for val in container_args.values():
            if "description" in val:
                val['description'] = ParsableText(val['description'].encode('utf-8').decode("unicode_escape"), 'rst').parse()

        return course, container_title, container_description, container_args, container_contest_args

    def page(self, course, container_title, container_description, container_args, container_contest_args, error=None, container_name="JPlag"):

        if "submissions" in container_args and container_args["submissions"]["type"] == "file":
            del container_args["submissions"]
        if "course" in container_args and container_args["course"]["type"] == "file":
            del container_args["course"]
        problems = [self.task_factory.get_task(course, x) for x in course.get_tasks()]
        self.template_helper.add_javascript(web.ctx.homepath + '/static/webapp/js/selectize.min.js', "header")
        self.template_helper.add_css(web.ctx.homepath + '/static/webapp/css/selectize.bootstrap3.css')
        self.template_helper.add_javascript(web.ctx.homepath + '/static/webapp/js/HoldOn.min.js', "header")
        self.template_helper.add_css(web.ctx.homepath + '/static/webapp/css/HoldOn.min.css')
        renderer = self.template_helper.get_custom_renderer('frontend/plugins/plagiarism')
        language = self.user_manager.session_language()
        return renderer.batch_create(course, container_name, container_title, container_description,
                                                                             container_args, problems, error, container_contest_args, language)


class CourseBatchJobDownload(INGIniousAdminPage):
    """ Get the file of a batch job """

    @property
    def batch_manager(self) -> BatchManager:
        """ Returns the plugin manager singleton """
        return self.app.batch_manager

    def GET_AUTH(self, courseid, bid, path=""):  # pylint: disable=arguments-differ
        """ GET request """

        self.get_course_and_check_rights(courseid) # simply verify rights
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
    def batch_manager(self) -> BatchManager:
        """ Returns the plugin manager singleton """
        return self.app.batch_manager

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



def add_admin_menu(course): # pylint: disable=unused-argument
    """ Add a menu for the plagiarism checker in the administration """
    return ("plagiarism", "<i class='fa fa-check-circle-o fa-fw'></i>&nbsp; Plagiarism")

def init(plugin_manager, _, client, conf):
    """
        Init the plugin.
        Available configuration in configuration.yaml:
        ::

            - plugin_module: "inginious.frontend.plugins.plagiarism"
            - storage_path: 'path/to/storage/results'
    """
    #page_pattern_course =  r'/admin/([^/]+)/plagiarism'
    #plugin_manager.add_page(page_pattern_course, PlagiarismPage)
    plugin_manager._app.batch_manager = BatchManager(client, plugin_manager.get_database(), plugin_manager._app.gridfs,
                                                     plugin_manager.get_submission_manager(), plugin_manager.get_user_manager(),
                                  plugin_manager._app.task_factory._filesystem.prefix)

    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism', CourseBatchOperations)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/create', CourseBatchJobCreate)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/summary/([^/]+)', CourseBatchJobSummary)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/grouped_summary/([^/]+)', GroupedListPage)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/download/([^/]+)', CourseBatchJobDownload)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/download/([^/]+)(/.*)', CourseBatchJobDownload)

    plugin_manager.add_hook('course_admin_menu', add_admin_menu)
    #plugin_manager.add_hook('course_menu', course_menu)
    #plugin_manager.add_hook('task_menu', task_menu)
