# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Manages plagiarism checks """
import os
import tempfile
import tarfile
import subprocess
import pymongo
import shutil

from datetime import datetime
from bson.objectid import ObjectId

from .constants import JPLAG_PATH, LANGUAGE_FILE_EXTENSION_MAP, LANGUAGE_PLAGIARISM_LANG_MAP, ALLOWED_ENVIRONMENTS


class PlagiarismManagerSingleton(object):
    """
        Manages batch jobs. Store them in DB and communicates with the inginious.backend to start them.
    """

    __instance = None

    @staticmethod
    def get_instance(database=None, gridfs=None, submission_manager=None, user_manager=None):
        """ Static access method. """
        if not PlagiarismManagerSingleton.__instance:
            PlagiarismManagerSingleton(database, gridfs, submission_manager, user_manager)
        return PlagiarismManagerSingleton.__instance

    def __init__(self, database, gridfs, submission_manager, user_manager):
        """ Virtually private constructor. """
        if PlagiarismManagerSingleton.__instance:
            raise Exception("This class is a singleton!")
        else:
            self._database = database
            self._gridfs = gridfs
            self._submission_manager = submission_manager
            self._user_manager = user_manager
            PlagiarismManagerSingleton.__instance = self

    def _get_submissions_data(self, course, task, plagiarism_language):
        """
        Return dict of best submissions for each student. The keys are the usernames and value is the submission.
        """
        users = self._user_manager.get_course_registered_users(course)
        task_name = task.get_name(self._user_manager.session_language())

        db_args = {"courseid": course.get_id(), "status": 'done', 'taskid': task.get_id()}

        submissions = {}
        for user in users:
            db_args['username'] = user
            user_submissions = list(self._database.submissions.find(
                db_args,
                projection=['_id', 'input', 'courseid', 'taskid', 'username'],
                sort=[('grade', pymongo.ASCENDING), ('submitted_on', pymongo.ASCENDING)]))
            for submission in user_submissions:
                # As the submissions are ordered, look for the best submission that matches the plagiarism language.
                try:
                    submission = self._submission_manager.get_input_from_submission(submission)
                except:
                    raise Exception(
                        _("An error occurred while retrieving submission from task {}.".format(task_name)))
                problem_id = self._get_submission_problem_id(submission['input'])
                type_task = submission['input'][problem_id + '/type']
                submission_language = submission['input'][problem_id + '/language']
                if type_task == 'notebook_file' and plagiarism_language == 'text':
                    submissions[user] = submission
                    break
                elif LANGUAGE_PLAGIARISM_LANG_MAP[submission_language] == plagiarism_language:
                    submissions[user] = submission
                    break

        if not submissions or len(submissions) < 2:
            raise Exception(_(
                "There are not enough submissions in task: {}, for the selected language. At least 2 students must have submitted to compare.".format(
                    task_name)))
        return submissions

    def _get_submission_problem_id(self, input_data):
        problem_id = filter(lambda x: '/' not in x, input_data.keys())
        problem_id = filter(lambda x: '@' not in x, problem_id)
        problem_id = list(problem_id)[0]
        return problem_id

    def _generate_submission_code_file(self, input_data, path, plagiarism_language):
        problem_id = self._get_submission_problem_id(input_data)
        code = input_data[problem_id]

        file_extension = LANGUAGE_FILE_EXTENSION_MAP[plagiarism_language]

        # If submission was notebook, the code is in code['value']
        if plagiarism_language == 'text' and type(code) == dict:
            code = code['value'].decode('utf-8')

        with open(os.path.join(path, 'code.{}'.format(file_extension)), 'w') as file:
            file.write(code)

    def _generate_base_code_file(self, base_code, path, plagiarism_language):
        file_extension = LANGUAGE_FILE_EXTENSION_MAP[plagiarism_language]

        template_dir = os.path.join(path, 'template')
        os.mkdir(template_dir)
        file_path = os.path.join(template_dir, 'template.{}'.format(file_extension))
        with open(file_path, 'w') as file:
            file.write(base_code)

    def _run_plagiarism(self, data):
        plagiarism_language = LANGUAGE_PLAGIARISM_LANG_MAP[data['language']]

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = '/home/uncode/Desktop/plagiarism'
            all_submissions_dir = os.path.join(tmp_dir, "all_submissions")
            try:
                os.mkdir(all_submissions_dir)
            except:
                shutil.rmtree(all_submissions_dir, ignore_errors=True)
                os.mkdir(all_submissions_dir)

            output_dir = os.path.join(tmp_dir, "output")
            try:
                os.mkdir(output_dir)
            except:
                shutil.rmtree(output_dir, ignore_errors=True)
                os.mkdir(output_dir)

            for user, submission in data["submissions"].items():
                user_dir = os.path.join(all_submissions_dir, user)
                os.mkdir(user_dir)

                self._generate_submission_code_file(submission['input'], user_dir, plagiarism_language)

            jplag_args = ["-s", '-l', plagiarism_language, "-r", output_dir, '-p',
                          LANGUAGE_FILE_EXTENSION_MAP[plagiarism_language]]

            # Write base code template file
            if data['base_code']:
                self._generate_base_code_file(data['base_code'], all_submissions_dir, plagiarism_language)
                jplag_args.append('-bc')
                jplag_args.append('template')

            jplag_args.append(all_submissions_dir)
            command = ["java", '-jar', JPLAG_PATH] + jplag_args

            completed_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = completed_process.stdout.decode()
            stderr = completed_process.stderr.decode()
            return_code = completed_process.returncode

            with open(os.path.join(output_dir, 'jplag_stdout.txt'), 'w') as stdout_file:
                stdout_file.write(stdout)
            with open(os.path.join(output_dir, 'jplag_stderr.txt'), 'w') as stderr_file:
                stderr_file.write(stderr)

            if return_code != 0:
                raise Exception(_("An error occurred while generating the plagiarism check."))

            # Store results in database with gridfs
            with tempfile.TemporaryFile() as file:
                tar = tarfile.open(fileobj=file, mode='w:gz')
                tar.add(output_dir, '/', True)
                tar.close()
                file.flush()
                file.seek(0)
                return return_code, stdout, stderr, self._gridfs.put(file)

    def add_plagiarism_check(self, course, data):
        """
            Add a job in the queue and returns a batch job id.
            inputdata is a dict containing all the keys of get_plagiarism_container_metadata(container_name)["parameters"] BUT the keys "course" and
            "submission" IF their
            type is "file". (the content of the course and the submission will be automatically included by this function.)
            The values associated are file-like objects for "file" types and  strings for "text" types.
        """
        task = data['task']
        if task.get_environment() not in ALLOWED_ENVIRONMENTS:
            return True, _(
                "Task environment is not available for plagiarism check: {}. Check the task is correctly configured.".format(
                    task.get_environment()))

        try:
            data["submissions"] = self._get_submissions_data(course, task,
                                                             LANGUAGE_PLAGIARISM_LANG_MAP[data['language']])
        except Exception as e:
            return True, str(e)

        try:
            return_code, stdout, stderr, results_file = self._run_plagiarism(data)
            if return_code == 0 and stderr:
                return_code = 1
        except Exception as e:
            return True, str(e)

        plagiarism_obj = {
            "result": {
                "stdout": stdout,
                "stderr": stderr,
                "retval": return_code,
                'file': results_file,
            },
            "courseid": course.get_id(),
            'container_name': task.get_name(self._user_manager.session_language()),
            "submitted_on": datetime.now(),
            "language": data['language']
        }
        self._database.batch_jobs.insert(plagiarism_obj)

        return False, None

    def get_plagiarism_check(self, check_id):
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
        return self._database.batch_jobs.find_one({"_id": ObjectId(check_id)})

    def get_all_plagiarism_checks_for_course(self, course_id):
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
        return list(self._database.batch_jobs.find({"courseid": course_id}))

    def drop_plagiarism_check(self, check_id):
        """ Delete a plagiarism check from database"""
        check = self._database.batch_jobs.find_one({"_id": ObjectId(check_id)})
        self._database.batch_jobs.remove({"_id": ObjectId(check_id)})
        if "file" in check["result"]:
            self._gridfs.delete(check["result"]["file"])
