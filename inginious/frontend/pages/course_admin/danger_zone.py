# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.


import datetime
import glob
import hashlib
import logging
import os
import random
import zipfile

import bson.json_util
import web

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage


class CourseDangerZonePage(INGIniousAdminPage):
    """ Course administration page: list of classrooms """
    _logger = logging.getLogger("inginious.webapp.danger_zone")
    _COLLECTIONS = {"aggregations", "user_tasks", "submissions", "plagiarism_checks"}

    def _wipe_course(self, courseid):
        submissions = self.database.submissions.find({"courseid": courseid})

        gridfs = self.submission_manager.get_gridfs()
        for submission in submissions:
            for key in ["input", "archive"]:
                if key in submission and type(submission[key]) == bson.objectid.ObjectId and gridfs.exists(
                        submission[key]):
                    gridfs.delete(submission[key])

        for collection_name in self._COLLECTIONS:
            collection = self.database[collection_name]
            if collection.find_one({"courseid": courseid}):
                collection.remove({"courseid": courseid})
            else:
                collection.remove({"course_id": courseid})

        self._logger.info("Course %s wiped.", courseid)

    def dump_course(self, courseid):
        """ Create a zip file containing all information about a given course in database and then remove it from db"""
        filepath = os.path.join(self.backup_dir, courseid, datetime.datetime.now().strftime("%Y%m%d.%H%M%S") + ".zip")

        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        with zipfile.ZipFile(filepath, "w", allowZip64=True) as zipf:
            for collection_name in self._COLLECTIONS:
                collection = self.database[collection_name]
                if collection_name == "submissions":
                    data = self._dump_submissions(zipf, courseid)
                elif collection.find_one({"courseid": courseid}):
                    data = collection.find({"courseid": courseid})
                else:
                    data = collection.find({"course_id": courseid})
                zipf.writestr("{}.json".format(collection_name), bson.json_util.dumps(data), zipfile.ZIP_DEFLATED)

        self._logger.info("Course %s dumped to backup directory.", courseid)
        self._wipe_course(courseid)

    def _dump_submissions(self, zipf, courseid):
        submissions = self.database.submissions.find({"courseid": courseid})
        erroneous_subs = set()

        gridfs = self.submission_manager.get_gridfs()
        for submission in submissions:
            for key in ["input", "archive"]:
                if key in submission and type(submission[key]) == bson.objectid.ObjectId:
                    if gridfs.exists(submission[key]):
                        infile = gridfs.get(submission[key])
                        zipf.writestr(key + "/" + str(submission[key]) + ".data", infile.read(),
                                      zipfile.ZIP_DEFLATED)
                    else:
                        self._logger.error(
                            "Missing {} in grifs, skipping submission {}".format(str(submission[key]),
                                                                                 str(submission["_id"])))
                        erroneous_subs.add(submission["_id"])

        submissions.rewind()
        return [submission for submission in submissions if submission["_id"] not in erroneous_subs]

    def restore_course(self, courseid, backup):
        """ Restores a course of given courseid to a date specified in backup (format : YYYYMMDD.HHMMSS) """
        self._wipe_course(courseid)

        filepath = os.path.join(self.backup_dir, courseid, backup + ".zip")
        with zipfile.ZipFile(filepath, "r") as zipf:

            for collection_name in self._COLLECTIONS:
                if collection_name == "submissions":
                    data = self._restore_submissions(zipf)
                else:
                    data = bson.json_util.loads(zipf.read("{}.json".format(collection_name)).decode("utf-8"))

                if len(data) > 0:
                    self.database[collection_name].insert(data)

        self._logger.info("Course %s restored from backup directory.", courseid)

    def _restore_submissions(self, zipf):
        submissions = bson.json_util.loads(zipf.read("submissions.json").decode("utf-8"))

        gridfs = self.submission_manager.get_gridfs()
        for submission in submissions:
            for key in ["input", "archive"]:
                if key in submission and type(submission[key]) == bson.objectid.ObjectId:
                    submission[key] = gridfs.put(zipf.read(key + "/" + str(submission[key]) + ".data"))

        return submissions

    def delete_course(self, courseid):
        """ Erase all course data """
        # Wipes the course (delete database)
        self._wipe_course(courseid)

        # Deletes the course from the factory (entire folder)
        self.course_factory.delete_course(courseid)

        # Removes backup
        filepath = os.path.join(self.backup_dir, courseid)
        if os.path.exists(os.path.dirname(filepath)):
            for backup in glob.glob(os.path.join(filepath, '*.zip')):
                os.remove(backup)

        self._logger.info("Course %s files erased.", courseid)

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        data = web.input()

        if "download" in data:
            filepath = os.path.join(self.backup_dir, courseid, data["download"] + '.zip')

            if not os.path.exists(os.path.dirname(filepath)):
                raise web.notfound()

            web.header('Content-Type', 'application/zip', unique=True)
            web.header('Content-Disposition', 'attachment; filename="' + data["download"] + '.zip' + '"', unique=True)

            return open(filepath, 'rb')

        else:
            return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        msg = ""
        error = False

        data = web.input()
        if not data.get("token", "") == self.user_manager.session_token():
            msg = _("Operation aborted due to invalid token.")
            error = True
        elif "wipeall" in data:
            if not data.get("courseid", "") == courseid:
                msg = _("Wrong course id.")
                error = True
            else:
                try:
                    self.dump_course(courseid)
                    msg = _("All course data have been deleted.")
                except:
                    msg = _("An error occurred while dumping course from database.")
                    error = True
        elif "restore" in data:
            if "backupdate" not in data:
                msg = "No backup date selected."
                error = True
            else:
                try:
                    dt = datetime.datetime.strptime(data["backupdate"], "%Y%m%d.%H%M%S")
                    self.restore_course(courseid, data["backupdate"])
                    msg = _("Course restored to date : ") + "{}.".format(dt.strftime("%Y-%m-%d %H:%M:%S"))
                except:
                    msg = _("An error occurred while restoring backup.")
                    error = True
        elif "deleteall" in data:
            if not data.get("courseid", "") == courseid:
                msg = _("Wrong course id.")
                error = True
            else:
                try:
                    self.delete_course(courseid)
                    web.seeother(self.app.get_homepath() + '/index')
                except:
                    msg = _("An error occurred while deleting the course data.")
                    error = True

        return self.page(course, msg, error)

    def get_backup_list(self, course):
        backups = []

        filepath = os.path.join(self.backup_dir, course.get_id())
        if os.path.exists(os.path.dirname(filepath)):
            for backup in glob.glob(os.path.join(filepath, '*.zip')):
                try:
                    basename = os.path.basename(backup)[0:-4]
                    dt = datetime.datetime.strptime(basename, "%Y%m%d.%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                    backups.append({"file": basename, "date": dt})
                except:  # Wrong format
                    pass

        return backups

    def page(self, course, msg="", error=False):
        """ Get all data and display the page """
        thehash = hashlib.sha512(str(random.getrandbits(256)).encode("utf-8")).hexdigest()
        self.user_manager.set_session_token(thehash)

        backups = self.get_backup_list(course)

        return self.template_helper.get_renderer().course_admin.danger_zone(course, thehash, backups, msg, error)
