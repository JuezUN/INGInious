# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
"""Notebooks grader serverless module"""

from hashlib import sha512
import datetime
import web
import json
import inginious.frontend.pages.api._api_page as api
from inginious.frontend.pages.api.courses import APICourses
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.common.course_factory import CourseNotFoundException
from inginious.frontend.plugins.analytics.analytics_collection_manager import AnalyticsCollectionManagerSingleton
from inginious.frontend.plugins.analytics.services_collection_manager import ServicesCollectionManagerSingleton

class NotebookGradingAPI(api.APIAuthenticatedPage):
    """
    API definition for get, set and delete grader of a test,
     
    """
    def API_GET(self): # pylint: disable=arguments-differ
        """GET: API get grader from a test of a task
            params: course_id: str
                    task_id: str
                    test_id: str
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
            if task_grader_info is None:
                raise api.APIError(404, "Grader not found")
            data = {
                "grader": task_grader_info['grader'],
                "functions_names_to_evaluate": task_grader_info['functions_names_to_evaluate'],
                "variables_names_to_evaluate": task_grader_info['variables_names_to_evaluate'],
                "updated_on": task_grader_info['updated_on'].strftime("%Y_%m_%d_%H_%M_%S"),
            }
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
        weight = get_mandatory_parameter(request_params, "weight")

        try:
            course = self.course_factory.get_course(course_id)
        except CourseNotFoundException as course_not_found:
            raise api.APINotFound("Course not found") from course_not_found

        course_staff = course.get_staff()

        username = self.user_manager.session_username()



        if username in course_staff:
            #Find if the grader with that id already exists
            try:
                old_grader = self.database.tasks_graders.find({
                    "courseid": course_id,
                    "taskid": task_id,
                    "testid": test_id,
                })
            except:
                raise api.APIError(500, "Server error")
            if old_grader.count() > 0:
                new_values = { "$set": {
                    "grader": grader,
                    "functions_names_to_evaluate": functions_names_to_evaluate,
                    "variables_names_to_evaluate": variables_names_to_evaluate,
                    "weight": float(weight),
                    "updated_on": datetime.datetime.utcnow(),
                }}
                self.database.tasks_graders.update_one({
                    "courseid": course_id,
                    "taskid": task_id,
                    "testid": test_id,
                }, new_values)
            else:
                self.database.tasks_graders.insert({
                    "courseid": course_id,
                    "taskid": task_id,
                    "testid": test_id,
                    "grader": grader,
                    "functions_names_to_evaluate": functions_names_to_evaluate,
                    "variables_names_to_evaluate": variables_names_to_evaluate,
                    "weight": float(weight),
                    "updated_on": datetime.datetime.utcnow(),
                })
            return 200, "ok"

        raise api.APIError(403, "You are not authorized to access this resource")

    def API_DELETE(self):
        """DELETE: API delete grader of a test of a task
            params: course_id
                    task_id
                    test_id
            returns: 200 and ok
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

        username = self.user_manager.session_username()

        if username in course_staff:
            #Delete the test
            try:
                self.database.tasks_graders.delete_one({
                    "courseid": course_id,
                    "taskid": task_id,
                    "testid": test_id,
                })
            except:
                raise api.APIError(500, "Server error")
            
            return 200, "ok"

        raise api.APIError(403, "You are not authorized to access this resource")
        
class NotebookGradersAPI(api.APIAuthenticatedPage):
    def API_GET(self): # pylint: disable=arguments-differ
        """
        GET: API get all test graders ids of a task
            params: course_id: str
                    task_id: str
            returns: 200 and task graders ids
        """
        request_params = web.input()

        course_id = get_mandatory_parameter(request_params, "course_id")
        task_id = get_mandatory_parameter(request_params, "task_id")

        try:
            course = self.course_factory.get_course(course_id)
        except CourseNotFoundException as course_not_found:
            raise api.APINotFound("Course not found") from course_not_found

        course_staff = course.get_staff()
        course_students = self.user_manager.get_course_registered_users(course, with_admins=False)

        username = self.user_manager.session_username()

        if username in course_students or username in course_staff:
            #Retrieve the graders
            try:
                task_graders = self.database.tasks_graders.find({
                    "courseid": course_id, 
                    "taskid": task_id
                })
            except:
                raise api.APIError(500, "Error finding courses")
            if task_graders.count() > 0:
                #Only return the ids
                data = [grader["testid"] for grader in task_graders]
            else:
                raise api.APIError(404, "No graders found")
            return 200, data

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
            
        def __get_tests_weights(self, course_id, task_id):
            """
            Get the weights of the tests of the given task
            A dictionary, keyed by the test_id, and value the weight
            """
            try:
                task_graders = self.database.tasks_graders.find({
                    "courseid": course_id, 
                    "taskid": task_id
                })
            except:
                raise api.APIError(500, "Server failed finding graders")
            return { grader["testid"]: grader.get("weight", 1) for grader in task_graders}
            
        def API_GET(self):
            """
            GET: API run test, just validate the signature, ensure test exists
            params: test_id: str
                    signature: int
            returns: 200 and ok
                     502 if error
            """
            username = self.user_manager.session_username()
            request_params = web.input()
            test_id = get_mandatory_parameter(request_params, "test_id")
            signature = get_mandatory_parameter(request_params, "signature")
            
            try:
                self.__validate_signature(username, test_id, signature)
            except:
                raise api.APIError(502, "Signature is invalid")
            return 200, "signature ok"

        def API_POST(self): # pylint: disable=arguments-differ
            """POST: API send submission, verify signature of each test, calculate the
            submission grade and insert the submission
            params: course_id: str
                    task_id: str
                    test_grade: int
                    result: str
                    status: str
                    results: dict
            returns: 200 and ok
            """
            username = self.user_manager.session_username()
            request_params = web.input()
            
            course_id = get_mandatory_parameter(request_params, "course_id")
            task_id = get_mandatory_parameter(request_params, "task_id")
            result = get_mandatory_parameter(request_params, "result")
            status = get_mandatory_parameter(request_params, "status")
            results = get_mandatory_parameter(request_params, "results")
            results = json.loads(results)
            
            
            #Validate signature for each test
            for test_id in results:
                test = results[test_id]
                self.__validate_signature(username, test["id"], test["signature"])
            #We calculate the submissions grade based on the test grades, 
            #we calculate weighted average
            tests_weights = self.__get_tests_weights(course_id,task_id)
            #grades is a list of tuples containing (grade, weight)
            grades = [(results[test_id]["test_grade"], tests_weights[test_id]) for test_id in results]
            #We ensure that the sum of weights is greater than zero
            sum_of_weights = sum([tests_weights[test_id] for test_id in results])
            sum_of_weights = sum_of_weights if sum_of_weights > 0 else 1
            #Calculate the grade
            submission_grade = sum([grade[0]*grade[1] for grade in grades]) / sum_of_weights
            #only two decimal
            submission_grade = round(submission_grade,2)
            #Retrieve course
            try:
                course = self.course_factory.get_course(course_id)
            except CourseNotFoundException as course_not_found:
                raise api.APINotFound("Course not found") from course_not_found
            #Retrieve course users
            course_staff = course.get_staff()
            course_students = self.user_manager.get_course_registered_users(course, with_admins=False)
            task = course.get_task(task_id)
            if username in course_students or username in course_staff:
                user_can_submit = self.user_manager.task_can_user_submit(task, username)
                
                #and check no periods on keys
                keys = list(results.keys())
                for test_id in keys:
                    test_id_no_period = test_id.replace(".", "")
                    results[test_id_no_period] = results.pop(test_id)   
                #submission information
                submission_info = {
                    "courseid": course_id,
                    "taskid": task_id,
                    "grade": submission_grade,
                    "result": result,
                    "status": status,
                    "grader_results": results,
                    "submitted_on": datetime.datetime.utcnow(),
                    "username": [username],
                    "custom": {
                        "custom_summary_result": "ACCEPTED" if submission_grade == 100.0 else "WRONG_ANSWER",
                    },
                    "response_type": "dict"
                }
                if user_can_submit:
                    #insert submission
                    submission = self.database.submissions.insert(submission_info)
                    #Update user stats
                    self.user_manager.update_user_stats(
                        username, 
                        task,
                        submission_info, 
                        result, 
                        submission_grade, 
                        newsub=True)
                    
                    #Add Sumbission Analytic
                    analytics_manager = AnalyticsCollectionManagerSingleton.get_instance()
                    services_manager = ServicesCollectionManagerSingleton.get_instance()
                    service = {
                        "key": "notebook_client_grader",
                        "name": "Notebook (External Grading) Submissions"
                    }
                    session_id = self.user_manager.session_id()
                    date = datetime.datetime.now()
                    analytics_manager.add_visit(service, username, date, session_id, course_id)
                    services_manager.add_service(service)
                    
                    return 200, "{}%".format(submission_grade)
                else:
                    msg = "not allowed to submit task, deadline reached or limit on number of submissions exceeded"
                    raise api.APIError(400, "{}".format(msg))
                    
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
    
class UserCoursesAPI(APICourses):
    def API_GET(self):  # pylint: disable=arguments-differ
        """
            List courses available to the connected client including the LTI courses
            Returns a dict in the form
            ::
                {
                    "courseid1":
                    {
                        "name": "Name of the course",     #the name of the course
                        "is_registered": False,           #indicates if the user is registered to this course or not
                        "tasks":                          #only appears if is_registered is True
                        {
                            "taskid1": "name of task1",
                            "taskid2": "name of task2"
                            #...
                        },
                        "grade": 0.0                      #the current grade in the course. Only appears if is_registered is True
                    }
                    #...
                }
        """
        output = []

        courses = self.course_factory.get_all_courses()
        
        username = self.user_manager.session_username()
        user_info = self.database.users.find_one({"username": username})

        for courseid, course in courses.items():
            if self.user_manager.course_is_open_to_user(course, username, False):
                data = {
                    "id": courseid,
                    "name": course.get_name(self.user_manager.session_language()),
                    "is_registered": self.user_manager.course_is_open_to_user(course, username, False)
                }
                data["tasks"] = {taskid: task.get_name(self.user_manager.session_language()) for taskid, task in course.get_tasks().items()}
                data["grade"] = self.user_manager.get_course_cache(username, course)["grade"]
                output.append(data)
            elif self.user_manager.course_is_open_to_user(course, username, True):#LTI courses
                data = {
                    "id": courseid,
                    "name": course.get_name(self.user_manager.session_language()),
                    "is_registered": self.user_manager.course_is_open_to_user(course, username, True)
                }
                data["tasks"] = {taskid: task.get_name(self.user_manager.session_language()) for taskid, task in course.get_tasks().items()}
                data["grade"] = self.user_manager.get_course_cache(username, course)["grade"]
                output.append(data)
        return 200, output

