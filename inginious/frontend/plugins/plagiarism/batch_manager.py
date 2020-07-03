# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Manages batch containers """
import logging
import os
import tempfile
import tarfile
from datetime import datetime
import subprocess
import shlex

from bson.objectid import ObjectId
import web


class BatchManager(object):
    """
        Manages batch jobs. Store them in DB and communicates with the inginious.backend to start them.
    """

    def __init__(self, client, database, gridfs, submission_manager, user_manager, task_directory):
        self._client = client
        self._database = database
        self._gridfs = gridfs
        self._submission_manager = submission_manager
        self._user_manager = user_manager
        self._task_directory = task_directory
        self._logger = logging.getLogger("inginious.batch")

    def _get_course_data(self, course):
        """ Returns a file-like object to a tgz archive of the course files """
        dir_path = os.path.join(self._task_directory, course.get_id())
        tmpfile = tempfile.TemporaryFile()
        tar = tarfile.open(fileobj=tmpfile, mode='w:gz')
        tar.add(dir_path, "/", True)
        tar.close()
        tmpfile.seek(0)
        return tmpfile

    def _get_submissions_data(self, course, tasks, folders, eval_only):
        """ Returns a file-like object to a tgz archive containing all the submissions made by the students for the course """
        users = self._user_manager.get_course_registered_users(course)

        db_args = {"courseid": course.get_id(), "username": {"$in": users}}
        if tasks is not None:
            db_args["taskid"] = {"$in": tasks}
        if eval_only:
            submissionsid = [user_task["submissionid"] for user_task in self._database.user_tasks.find(db_args)]
            submissions = list(self._database.submissions.find({"_id": {"$in": submissionsid}}))
        else:
            submissions = list(self._database.submissions.find(db_args))
        return self._submission_manager.get_submission_archive(submissions, list(reversed(folders.split('/'))), {})

    def get_batch_container_metadata(self, container_name):
        """
            Returns the arguments needed by a particular batch container.
            :returns: a tuple in the form
                ("container title",
                 "container description in restructuredtext",
                 {"key":
                    {
                     "type:" "file", #or "text",
                     "path": "path/to/file/inside/input/dir", #not mandatory in file, by default "key"
                     "name": "name of the field", #not mandatory in file, default "key"
                     "description": "a short description of what this field is used for", #not mandatory, default ""
                     "custom_key1": "custom_value1",
                     ...
                    }
                 }
                )
        """
        if container_name not in self._client.get_batch_containers_metadata():
            raise Exception("This batch container is not allowed to be started")

        metadata = self._client.get_batch_containers_metadata()[container_name]
        if metadata != (None, None, None):
            metadata = (container_name, metadata["description"], metadata["parameters"])
        return metadata


    def add_batch_job(self, course, inputdata, launcher_name=None, send_mail=None):
        """
            Add a job in the queue and returns a batch job id.
            inputdata is a dict containing all the keys of get_batch_container_metadata(container_name)["parameters"] BUT the keys "course" and
            "submission" IF their
            type is "file". (the content of the course and the submission will be automatically included by this function.)
            The values associated are file-like objects for "file" types and  strings for "text" types.
        """

        # Download the course content and submissions and add them to the input
        inputdata["course"] = self._get_course_data(course)

        tasks = [str(inputdata["task"])]

        inputdata["submissions"] = self._get_submissions_data(course, tasks, 'taskid/username', "1")
        print(str(inputdata["submissions"]))
        obj = {
            "courseid": course.get_id(),
            'container_name': inputdata["real_title"],
            "submitted_on": datetime.now(),
            "group_name": inputdata.get("group_name",''),
            "group_hash": inputdata.get("group_hash", '')
        }

        batch_job_id = self._database.batch_jobs.insert(obj)

        launcher_name = launcher_name or "plugin"

        #EJECUTAR JPLAG AQUÍ
        data = web.input()
        plagiarism = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "plagiarism")
        script = os.path.join(plagiarism, "script.sh")
        with tempfile.TemporaryDirectory() as tmpdirname:
            #tmpdirname = ""
            inp = os.path.join(tmpdirname, "input")
            os.mkdir(inp)
            out = os.path.join(tmpdirname, "output")
            os.mkdir(out)
            course_tgz = inputdata["course"].readlines()
            submissions_tgz = inputdata["submissions"].readlines()
            with open(os.path.join(inp, "course.tgz"), 'wb') as file:
                for line in course_tgz:
                    file.write(line)
            with open(os.path.join(inp, "submissions.tgz"), 'wb') as file:
                for line in submissions_tgz:
                    file.write(line)
            with open(os.path.join(inp, "task.txt"), 'w') as file:
                file.write(inputdata["task"])
            retval = subprocess.call(shlex.split("/bin/bash " + script+" "+tmpdirname+" "+plagiarism + " " + data.get('language', 'python3')))
            try:
                stdout = open(os.path.join(out, "jplag_stdout.txt"), "r").read()
                stderr = open(os.path.join(out, "jplag_stderr.txt"), "r").read()
            except:
                stdout = "No output"
                stderr = "No output"
            with tempfile.TemporaryFile() as file:

                tar = tarfile.open(fileobj=file, mode='w:gz')
                tar.add(out, '/', True)
                tar.close()
                file.flush()
                file.seek(0)
                self._batch_job_done_callback(batch_job_id, retval, stdout, stderr, file)

        #self._client.new_batch_job("JPlag", inputdata,
                                   #lambda retval, stdout, stderr, file:
                                   #self._batch_job_done_callback(batch_job_id, retval, stdout, stderr, file, send_mail),
                                   #launcher_name="Frontend - {}".format(launcher_name))

        return batch_job_id

    def _batch_job_done_callback(self, batch_job_id, retval, stdout, stderr, file, send_mail=None):
        """ Called when the batch job with id jobid has finished.
            :param retval: an integer, the return value of the command in the container
            :param stdout: stdout of the container
            :param stderr: stderr of the container
            :param file: tgz as bytes. Can be None if retval < 0
        """

        result = {
            "retval": retval,
            "stdout": stdout,
            "stderr": stderr,
        }
        if file is not None:
            result["file"] = self._gridfs.put(file)

        # Save submission to database
        self._database.batch_jobs.update(
            {"_id": batch_job_id},
            {"$set": {"result": result}}
        )

        # Send a mail to user
        if send_mail is not None:
            try:
                web.sendmail(web.config.smtp_sendername, send_mail, "Batch job {} finished".format(batch_job_id),
                             """This is an automated message.

The batch job you launched on UNCode is done. You can see the results on the "batch operation" page of your course
administration.""")
            except Exception as e:
                self._logger.error("Cannot send mail: " + str(e))

    def get_batch_job_status(self, batch_job_id):
        """ Returns the batch job with id batch_job_id Batch jobs are dicts in the form
            {"courseid": "...", "container_name": "..."} if the job is still ongoing, and
            {"courseid": "...", "container_name": "...", "results": {}} if the job is done.
            the dict result can be either:

            - {"retval":0, "stdout": "...", "stderr":"...", "file":"..."}
                if everything went well. (file is an gridfs id to a tgz file)
            - {"retval":"...", "stdout": "...", "stderr":"..."}
                if the container crashed (retval is an int != 0) (can also contain file, but not mandatory)
            - {"retval":-1, "stderr": "the error message"}
                if the container failed to start
        """
        return self._database.batch_jobs.find_one({"_id": ObjectId(batch_job_id)})

    def get_all_batch_jobs_for_course(self, course_id):
        """ Returns all the batch jobs for the course course id. Batch jobs are dicts in the form
            {"courseid": "...", "container_name": "...", "submitted_on":"..."} if the job is still ongoing, and
            {"courseid": "...", "container_name": "...", "submitted_on":"...", "results": {}} if the job is done.
            the dict result can be either:

            - {"retval":0, "stdout": "...", "stderr":"...", "file":"..."}
                if everything went well. (file is an gridfs id to a tgz file)
            - {"retval":"...", "stdout": "...", "stderr":"..."}
                if the container crashed (retval is an int != 0) (can also contain file, but not mandatory)
            - {"retval":-1, "stderr": "the error message"}
                if the container failed to start
        """
        return list(self._database.batch_jobs.find({"courseid": course_id, "group_name": ""}))

    def get_all_grouped_batch_jobs_for_course(self, course_id):
        """ Returns all the batch jobs for the course course id. Batch jobs are dicts in the form
            {"courseid": "...", "container_name": "...", "submitted_on":"..."} if the job is still ongoing, and
            {"courseid": "...", "container_name": "...", "submitted_on":"...", "results": {}} if the job is done.
            the dict result can be either:

            - {"retval":0, "stdout": "...", "stderr":"...", "file":"..."}
                if everything went well. (file is an gridfs id to a tgz file)
            - {"retval":"...", "stdout": "...", "stderr":"..."}
                if the container crashed (retval is an int != 0) (can also contain file, but not mandatory)
            - {"retval":-1, "stderr": "the error message"}
                if the container failed to start
        """
        return list(self._database.batch_jobs.find({"courseid": course_id, "group_name": {"$ne": ""}}))


    def get_all_grouped_batch_jobs_for_course_and_hash(self, course_id, group_hash):
        """ Returns all the batch jobs for the course course id. Batch jobs are dicts in the form
            {"courseid": "...", "container_name": "...", "submitted_on":"..."} if the job is still ongoing, and
            {"courseid": "...", "container_name": "...", "submitted_on":"...", "results": {}} if the job is done.
            the dict result can be either:

            - {"retval":0, "stdout": "...", "stderr":"...", "file":"..."}
                if everything went well. (file is an gridfs id to a tgz file)
            - {"retval":"...", "stdout": "...", "stderr":"..."}
                if the container crashed (retval is an int != 0) (can also contain file, but not mandatory)
            - {"retval":-1, "stderr": "the error message"}
                if the container failed to start
        """
        return list(self._database.batch_jobs.find({"courseid": course_id, "group_hash": group_hash}))

    def drop_batch_job(self, batch_job_id):
        """ Delete a **finished** batch job from the database """
        job = self._database.batch_jobs.find_one({"_id": ObjectId(batch_job_id)})
        if "result" not in job:
            raise Exception("Plagiarism check is still running, cannot delete it")
        self._database.batch_jobs.remove({"_id": ObjectId(batch_job_id)})
        if "file" in job["result"]:
            self._gridfs.delete(job["result"]["file"])


    def drop_grouped_batch_job(self, group_hash_id):
        """ Delete a **finished** batch job from the database """
        self._database.batch_jobs.remove({"group_hash": group_hash_id})

