import web
import os
from inginious.frontend.plugins.rubric_scoring.pages.api.rubric_wdo import RubricWdo
from bson.objectid import ObjectId
from pymongo import MongoClient
import gridfs

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from collections import OrderedDict

_BASE_RENDERER_PATH = 'frontend/plugins/rubric_scoring/pages/templates'
_BASE_RENDERER_PATH_TEMP = 'frontend/plugins/rubric_scoring_temp/pages/templates'

_BASE_STATIC_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../static')


def rubric_course_admin_menu_hook_temp(course):
    return "rubric_scoring_temp", '<i class="fa fa-bar-chart" aria-hidden="true"></i> Rubric Scoring Temp'


def rubric_course_admin_menu_hook(course):
    return "rubric_scoring", '<i class="fa fa-bar-chart" aria-hidden="true"></i> Rubric Scoring'


# listado de task
class CourseTaskListPage(INGIniousAdminPage):
    """ List informations about all tasks """

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, _ = self.get_course_and_check_rights(courseid)
        return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, _ = self.get_course_and_check_rights(courseid)
        data = web.input(task=[])

        if "task" in data:
            # Change tasks order
            for index, taskid in enumerate(data["task"]):
                try:
                    task = self.task_factory.get_task_descriptor_content(courseid, taskid)
                    task["order"] = index
                    self.task_factory.update_task_descriptor_content(courseid, taskid, task)
                except:
                    pass

        return self.page(course)

    def submission_url_generator(self, taskid):
        """ Generates a submission url """
        return "?format=taskid%2Fusername&tasks=" + taskid

    def page(self, course):
        """ Get all data and display the page """
        url = 'rubric_scoring'
        data = list(self.database.user_tasks.aggregate(
            [
                {
                    "$match":
                        {
                            "courseid": course.get_id(),
                            "username": {"$in": self.user_manager.get_course_registered_users(course, False)}
                        }
                },
                {
                    "$group":
                        {
                            "_id": "$taskid",
                            "viewed": {"$sum": 1},
                            "attempted": {"$sum": {"$cond": [{"$ne": ["$tried", 0]}, 1, 0]}},
                            "attempts": {"$sum": "$tried"},
                            "succeeded": {"$sum": {"$cond": ["$succeeded", 1, 0]}}
                        }
                }
            ]))

        # Load tasks and verify exceptions
        files = self.task_factory.get_readable_tasks(course)
        output = {}
        errors = []
        for task in files:
            try:
                output[task] = course.get_task(task)
            except Exception as inst:
                errors.append({"taskid": task, "error": str(inst)})
        tasks = OrderedDict(sorted(list(output.items()), key=lambda t: (t[1].get_order(), t[1].get_id())))

        # Now load additional informations
        result = OrderedDict()
        for taskid in tasks:
            result[taskid] = {"name": tasks[taskid].get_name(self.user_manager.session_language()), "viewed": 0,
                              "attempted": 0, "attempts": 0, "succeeded": 0,
                              "url": self.submission_url_generator(taskid)}

        for entry in data:
            if entry["_id"] in result:
                result[entry["_id"]]["viewed"] = entry["viewed"]
                result[entry["_id"]]["attempted"] = entry["attempted"]
                result[entry["_id"]]["attempts"] = entry["attempts"]
                result[entry["_id"]]["succeeded"] = entry["succeeded"]

        return self.template_helper.get_custom_renderer(_BASE_RENDERER_PATH).task_list(course, result, errors, url)


# Listado de submissions
class TaskListSubmissionPage(INGIniousAdminPage):
    def GET_AUTH(self, course_id, task_id):

        course, task = self.get_course_and_check_rights(course_id, task_id)

        self.template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-1.30.0.min.js")
        self.template_helper.add_javascript("https://cdn.jsdelivr.net/npm/lodash@4.17.4/lodash.min.js")

        return self.page(course, task_id, task)

    def page(self, course, task_id, task):
        """ Get all data and display the page """

        url = 'rubric_scoring'

        result = list(self.database.submissions.aggregate(

            [
                {
                    "$match":
                        {
                            "courseid": course.get_id(),
                            "taskid": task_id,
                            "username": {"$in": self.user_manager.get_course_registered_users(course, False)},

                        }
                },
                {
                  "$lookup":
                      {
                          "from": "users",
                          "localField": "username",
                          "foreignField": "username",
                          "as": "user_info"
                      }
                },
                {
                    "$replaceRoot": {"newRoot": {"$mergeObjects": [{"$arrayElemAt": ["$user_info", 0]}, "$$ROOT"]}}
                },

                {
                    "$project": {
                        "taskid": 1,
                        "username": 1,
                        "realname": 1
                    }
                },


            ]))

        # get task name
        task_name = course.get_task(task_id).get_name(self.user_manager.session_language())

        data = OrderedDict()
        for entry in result:
            data[entry["username"][0]] = {"username": entry["username"][0], "realname": entry["realname"]}

        return (
            self.template_helper.get_custom_renderer(_BASE_RENDERER_PATH).task_admin_rubric(
                course, data, task, task_name, url)
        )


class SubmissionRubricPage(INGIniousAdminPage):

    def POST_AUTH(self, course_id, task_id, submission_id):
        """ POST request """
        course, task = self.get_course_and_check_rights(course_id, task_id)
        data = web.input()

        if "grade" in data:
            self.database.submissions.update(
                {"_id": ObjectId(submission_id)},
                {"$set": {"custom.rubric_score": data["grade"]}
                 })
        elif "comment" in data:
            self.database.submissions.update(
                {"_id": ObjectId(submission_id)},
                {"$set": {"custom.comment": data["comment"]}
                 })

        return self.page(course, task, submission_id)

    def GET_AUTH(self, course_id, task_id, submission_id):
        course, task = self.get_course_and_check_rights(course_id, task_id)

        self.template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-1.30.0.min.js")
        self.template_helper.add_javascript("https://cdn.jsdelivr.net/npm/lodash@4.17.4/lodash.min.js")
        self.template_helper.add_css("static/css/rubric_scoring.css")

        return self.page(course, task, submission_id)

    def page(self, course, task, submission_id):

        # TODO: verificar que exista exactamente un elemento. TOMAR MEDIDAS PREVENTIVAS EN CASO CONTRARIO
        problem_id = task.get_problems()[0].get_id()

        submission = self.submission_manager.get_submission(submission_id, user_check=False)
        submission_input = self.submission_manager.get_input_from_submission(submission)

        comment = ""
        if ('custom' in submission and 'comment' in submission['custom']):
            comment = submission['custom']['comment']

        score = "No grade"
        if ('custom' in submission and 'rubric_score' in submission['custom']):
            score = submission['custom']['rubric_score']

        language = submission_input['input'][problem_id + '/language']
        data = {
            "url": 'rubric_scoring',

            "memory": "not memory",
            "test_passed": "no test casses",
            "verdict": "verdict"

        }

        import os
        dir_path = os.path.dirname(os.path.realpath(__file__))

        # raise Exception("PATH" + dir_path)
        rubric_wdo = RubricWdo('inginious/frontend/plugins/rubric_scoring/static/json/rubric.json')

        return (
            self.template_helper.get_custom_renderer(_BASE_RENDERER_PATH).submission_rubric(
                course, task, submission_input, problem_id,
                rubric_wdo.read_data('inginious/frontend/plugins/rubric_scoring/static/json/rubric.json'), data, language, comment,
                score)
        )


# listado de task
class CourseTaskListPageTemp(INGIniousAdminPage):
    """ List informations about all tasks """

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, _ = self.get_course_and_check_rights(courseid)
        return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, _ = self.get_course_and_check_rights(courseid)
        data = web.input(task=[])

        if "task" in data:
            # Change tasks order
            for index, taskid in enumerate(data["task"]):
                try:
                    task = self.task_factory.get_task_descriptor_content(courseid, taskid)
                    task["order"] = index
                    self.task_factory.update_task_descriptor_content(courseid, taskid, task)
                except:
                    pass

        return self.page(course)

    def submission_url_generator(self, taskid):
        """ Generates a submission url """
        return "?format=taskid%2Fusername&tasks=" + taskid

    def page(self, course):
        """ Get all data and display the page """
        url = 'rubric_scoring_temp'

        data = list(self.database.user_tasks.aggregate(
            [
                {
                    "$match":
                        {
                            "courseid": course.get_id(),
                            "username": {"$in": self.user_manager.get_course_registered_users(course, False)}
                        }
                },
                {
                    "$group":
                        {
                            "_id": "$taskid",
                            "viewed": {"$sum": 1},
                            "attempted": {"$sum": {"$cond": [{"$ne": ["$tried", 0]}, 1, 0]}},
                            "attempts": {"$sum": "$tried"},
                            "succeeded": {"$sum": {"$cond": ["$succeeded", 1, 0]}}
                        }
                }
            ]))

        # Load tasks and verify exceptions
        files = self.task_factory.get_readable_tasks(course)
        output = {}
        errors = []
        for task in files:
            try:
                output[task] = course.get_task(task)
            except Exception as inst:
                errors.append({"taskid": task, "error": str(inst)})
        tasks = OrderedDict(sorted(list(output.items()), key=lambda t: (t[1].get_order(), t[1].get_id())))

        # Now load additional informations
        result = OrderedDict()
        for taskid in tasks:
            result[taskid] = {"name": tasks[taskid].get_name(), "viewed": 0, "attempted": 0, "attempts": 0,
                              "succeeded": 0,
                              "url": self.submission_url_generator(taskid)}

        for entry in data:
            if entry["_id"] in result:
                result[entry["_id"]]["viewed"] = entry["viewed"]
                result[entry["_id"]]["attempted"] = entry["attempted"]
                result[entry["_id"]]["attempts"] = entry["attempts"]
                result[entry["_id"]]["succeeded"] = entry["succeeded"]

        return self.template_helper.get_custom_renderer(_BASE_RENDERER_PATH).task_list(course, result, errors, url)


class TaskListSubmissionPageTemp(INGIniousAdminPage):
    def GET_AUTH(self, course_id, task_id):

        course, task = self.get_course_and_check_rights(course_id, task_id)

        self.template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-1.30.0.min.js")
        self.template_helper.add_javascript("https://cdn.jsdelivr.net/npm/lodash@4.17.4/lodash.min.js")

        return self.page(course, task_id, task)

    def page(self, course, task_id, task):
        """ Get all data and display the page """
        # print(self.database.collection_names())
        print("here", course.get_id(), task_id)
        url = 'rubric_scoring_temp'

        result = list(self.database.submissions_rubric.aggregate(

            [
                {
                    "$match":
                        {
                            "courseid": course.get_id(),
                            "taskid": task_id,
                            "username": {"$in": self.user_manager.get_course_registered_users(course, False)},

                        }
                },
                {
                    "$project": {

                        "taskid": 1,
                        "veredict": 1,
                        "submitted_on": 1,
                        "username": 1,
                        "custom": 1

                    }
                }

            ]))

        print("result", result)
        data = OrderedDict()

        for entry in result:
            data[entry["_id"]] = {"taskid": entry["taskid"], "result": entry["veredict"], "_id": entry["_id"],
                                  "username": entry["username"], "date": entry["submitted_on"],
                                  "codeforces_id": entry["custom"]["codeforces_id"]}

            if "rubric_score" not in entry["custom"]:
                data[entry["_id"]]["rubric_score"] = "not grade"

            else:
                data[entry["_id"]]["rubric_score"] = entry["custom"]["rubric_score"]

        # print ("data -> ",data)
        return (
            self.template_helper.get_custom_renderer(_BASE_RENDERER_PATH).task_admin_rubric(
                course, data, task, url)
        )


class SubmissionRubricPageTemp(INGIniousAdminPage):
    client = MongoClient()
    database = client['INGInious']
    fs = gridfs.GridFS(database)

    def POST_AUTH(self, course_id, task_id, submission_id):
        """ POST request """
        course, task = self.get_course_and_check_rights(course_id, task_id)
        data = web.input()
        print("data->", data)
        self.database.submissions_rubric.update(
            {"_id": ObjectId(submission_id)},
            {"$set": {"custom.rubric_score": data["grade"]}
             })

        return self.page(course, task, submission_id)

    def GET_AUTH(self, course_id, task_id, submission_id):
        course, task = self.get_course_and_check_rights(course_id, task_id)

        self.template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-1.30.0.min.js")
        self.template_helper.add_javascript("https://cdn.jsdelivr.net/npm/lodash@4.17.4/lodash.min.js")
        self.template_helper.add_css("static/css/rubric_scoring.css")

        return self.page(course, task, submission_id)

    def get_submission(self, submissionid):
        """ Get a submission from the database """
        sub = self.database.submissions_rubric.find_one({'_id': ObjectId(submissionid)})

        return sub

    def page(self, course, task, submission_id):

        # TODO: verificar que exista exactamente un elemento. TOMAR MEDIDAS PREVENTIVAS EN CASO CONTRARIO
        problem_id = task.get_problems()[0].get_id()

        submission = self.get_submission(submission_id)

        comment = ""
        if ('custom' in submission and 'comment' in submission['custom']):
            comment = submission['custom']['comment']

        score = "No grade"
        if ('custom' in submission and 'rubric_score' in submission['custom']):
            score = submission['custom']['rubric_score']

        submission_input = self.submission_manager.get_input_from_submission(submission)
        print("submission_code", submission_input)
        print("------------")

        language = submission_input['language']

        data = {
            "url": 'rubric_scoring_temp',

            "memory": submission_input['memory'],
            "test_passed": submission_input['test_passed'],
            "verdict": submission_input['veredict']

        }

        rubric_wdo = RubricWdo('inginious/frontend/plugins/rubric_scoring/static/json/rubric.json')

        return (
            self.template_helper.get_custom_renderer(_BASE_RENDERER_PATH).submission_rubric(
                course, task, submission_input, problem_id, rubric_wdo, data, language, comment.strip(), score)
        )
