# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
"""Notebooks grader serverless module"""

import inginious.frontend.pages.api._api_page as api
from inginious.frontend.plugins.utils import get_mandatory_parameter
from hashlib import sha512
import datetime

import web

class NotebookGradingAPI(api.APIAuthenticatedPage):
    """API definition for get and set grader of a test"""

    def API_GET(self): # pylint: disable=arguments-differ
        request_params = web.input()

        course_id = get_mandatory_parameter(request_params, "course_id")
        task_id = get_mandatory_parameter(request_params, "task_id")
        test_id = get_mandatory_parameter(request_params, "test_id")

        try:
            course = self.course_factory.get_course(course_id)
        except:
            raise api.APINotFound("Course not found")

        course_staff = course.get_staff()
        course_students = self.user_manager.get_course_registered_users(
            course, with_admins=False)

        username = self.user_manager.session_username()

        if username in course_students and username not in course_staff:
            task_grader_info = self.database.tasks_graders.find_one(
                {"courseid": course_id, "taskid": task_id, "testid": test_id})

            data = {"grader": task_grader_info['grader'],
                    "functions_names_to_evaluate": task_grader_info['functions_names_to_evaluate'],
                    "variables_names_to_evaluate": task_grader_info['variables_names_to_evaluate'], }
            return 200, data

        raise api.APIError(403, "You are not authorized to access this resource")

    def API_POST(self): # pylint: disable=arguments-differ
        request_params = web.input()
        course_id = get_mandatory_parameter(request_params, "course_id")
        task_id = get_mandatory_parameter(request_params, "task_id")
        test_id = get_mandatory_parameter(request_params, "test_id")
        grader = get_mandatory_parameter(request_params, "grader")
        functions_names_to_evaluate = get_mandatory_parameter(
            request_params, "functions_names_to_evaluate")
        variables_names_to_evaluate = get_mandatory_parameter(
            request_params, "variables_names_to_evaluate")

        try:
            course = self.course_factory.get_course(course_id)
        except:
            raise api.APINotFound("Course not found")

        course_staff = course.get_staff()

        username = self.user_manager.session_username()

        if username in course_staff:
            self.database.tasks_graders.insert({
                "courseid": course_id,
                "taskid": task_id,
                "testid": test_id,
                "grader": grader,
                "functions_names_to_evaluate": functions_names_to_evaluate,
                "variables_names_to_evaluate": variables_names_to_evaluate,
            })
        else:
            raise api.APIError(403,"You are not authorized to access this resource")
        return 200, "ok"


class TestNotebookSubmissionAPI(api.APIAuthenticatedPage):
    """API definition for do a task submission"""
    

    def API_POST(self): # pylint: disable=arguments-differ
        username = self.user_manager.session_username()
        request_params = web.input()
        key_pair = (21145511420371257813590140607336605957103837517313322171470569706522561078664828667841325420528210362468905108841125312669175005069500260639399524062088068077504886974238207595257939432080569521137929147283808065912176990793482520433509116193089755149147387487723390391027270618541358331177840776511466141865612694492886915003526250148237699853388470861789974698225599828490908590893420408349423232934532594271550334201111542866305882684250049655689974023238891768700417170450261796942657506147044880425518280799814370090400325636947828503138490220047142351466235659660318214368333513255579788205983539615293773042251,65537)
        course_id = get_mandatory_parameter(request_params, "course_id")
        task_id = get_mandatory_parameter(request_params, "task_id")
        test_id = get_mandatory_parameter(request_params, "test_id")
        test_grade = get_mandatory_parameter(request_params, "test_grade")
        result = get_mandatory_parameter(request_params, "result")
        status = get_mandatory_parameter(request_params, "status")
        test_grade_message = get_mandatory_parameter(
            request_params, "test_grade_message")
        functions_source_code = get_mandatory_parameter(
            request_params, "functions_source_code")
        variables_source_code = get_mandatory_parameter(
            request_params, "variables_source_code")
        signature = get_mandatory_parameter(
            request_params, "signature")
        msg = 'UNCode_notebook_grader.'+username+'.'+test_id
        msg = str.encode(msg, encoding='utf-8')
        hash_msg = int.from_bytes(sha512(msg).digest(), byteorder='big')
        hash_from_signature = pow(int(signature), key_pair[1], key_pair[0])

        if hash_msg != hash_from_signature:
            raise api.APIError(502, "Signature is invalid")

        try:
            course = self.course_factory.get_course(course_id)
        except:
            raise api.APINotFound("Course not found")

        course_staff = course.get_staff()
        course_students = self.user_manager.get_course_registered_users(
            course, with_admins=False)

        if username in course_students and username not in course_staff:
            self.database.submissions.insert({
                "courseid": course_id,
                "taskid": task_id,
                "testid": test_id,
                "grade": test_grade,
                "result": result,
                "status": status,
                "test_grade_message": test_grade_message,
                "functions_source_code": functions_source_code,
                "variables_source_code": variables_source_code,
                "submitted_on": datetime.datetime.utcnow(),
                "username": [username]
                })
            return 200, "ok"
        
        raise api.APIError(403, "You are not authorized to access this resource")


class UserRolesAPI(api.APIAuthenticatedPage):
    """API definition for get user auth roles"""
    def API_GET(self): # pylint: disable=arguments-differ
        request_params = web.input()
        course_id = get_mandatory_parameter(request_params, "course_id")
        try:
            course = self.course_factory.get_course(course_id)
        except:
            raise api.APINotFound("Course not found")
        roles = self.user_manager.user_roles(course)
        return 200, {"roles": roles}
