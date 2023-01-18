# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
"""Notebooks grader serverless module"""

from hashlib import sha512
import datetime
import web
import inginious.frontend.pages.api._api_page as api
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.common.course_factory import CourseNotFoundException

class NotebookGradingAPI(api.APIAuthenticatedPage):
    """API definition for get and set grader of a test"""

    def API_GET(self): # pylint: disable=arguments-differ
        """GET: API get grader from a test of a task
            params: course_id
                    task_id
                    test_id
            returns: 200 and task grader, functions names to evaluate and variables names to evaluate
        """
        request_params = web.input()

        course_id = get_mandatory_parameter(request_params, "course_id")
        task_id = get_mandatory_parameter(request_params, "task_id")
        test_id = get_mandatory_parameter(request_params, "test_id")

        try:
            course = self.course_factory.get_course(course_id)
        except CourseNotFoundException as course_not_found:
            raise api.APINotFound("Course not found") from course_not_found

        course_staff = course.get_staff()
        course_students = self.user_manager.get_course_registered_users(
            course, with_admins=False)

        username = self.user_manager.session_username()

        if username in course_students or username in course_staff:
            task_grader_info = self.database.tasks_graders.find_one(
                {"courseid": course_id, "taskid": task_id, "testid": test_id})

            data = {"grader": task_grader_info['grader'],
                    "functions_names_to_evaluate": task_grader_info['functions_names_to_evaluate'],
                    "variables_names_to_evaluate": task_grader_info['variables_names_to_evaluate'], }
            return 200, data

        raise api.APIError(403, "You are not authorized to access this resource")

    def API_POST(self): # pylint: disable=arguments-differ
        """POST: API set grader of a test of a task
            params: course_id
                    task_id
                    test_id
                    grader(encrypted)
                    functions_names_to_evaluate
                    variables_names_to_evaluate
            returns: 200 and ok
        """
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
        except CourseNotFoundException as course_not_found:
            raise api.APINotFound("Course not found") from course_not_found

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
            return 200, "ok"

        raise api.APIError(403, "You are not authorized to access this resource")

def notebook_submission(public_key):
    """Task submission using the public key info for security assurance"""

    class TestNotebookSubmissionAPI(api.APIAuthenticatedPage):
        """API definition for do a task submission"""

        def __validate_signature(self, username, test_id, signature):
            """Validates signature using public key info"""
            msg = 'UNCode_notebook_grader.'+username+'.'+test_id
            msg = str.encode(msg, encoding='utf-8')
            hash_msg = int.from_bytes(sha512(msg).digest(), byteorder='big')
            hash_from_signature = pow(int(signature), public_key[1], public_key[0])

            if hash_msg != hash_from_signature:
                raise api.APIError(502, "Signature is invalid")

        def API_POST(self): # pylint: disable=arguments-differ
            """POST: API send submission
            params: course_id
                    task_id
                    test_id
                    test_grade
                    result
                    status
                    test_grade_message
                    functions_source_code
                    variables_source_code
                    signature
            returns: 200 and ok
            """
            username = self.user_manager.session_username()
            request_params = web.input()
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

            self.__validate_signature(username, test_id, signature)
            try:
                course = self.course_factory.get_course(course_id)
            except CourseNotFoundException as course_not_found:
                raise api.APINotFound("Course not found") from course_not_found

            course_staff = course.get_staff()
            course_students = self.user_manager.get_course_registered_users(
                course, with_admins=False)

            if username in course_students or username in course_staff:
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

    return TestNotebookSubmissionAPI


class UserRolesAPI(api.APIAuthenticatedPage):
    """API definition for get user auth roles"""
    def API_GET(self): # pylint: disable=arguments-differ
        """GET: API get roles from authenticated user of a course
            params: course_id
            returns: 200 and a list of roles
        """
        request_params = web.input()
        course_id = get_mandatory_parameter(request_params, "course_id")
        try:
            course = self.course_factory.get_course(course_id)
        except CourseNotFoundException as course_not_found:
            raise api.APINotFound("Course not found") from course_not_found
        roles = self.user_manager.user_roles(course)
        return 200, {"roles": roles}
