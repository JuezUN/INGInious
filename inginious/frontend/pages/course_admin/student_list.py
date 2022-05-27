# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

from collections import OrderedDict
import web

from inginious.frontend.pages.course_admin.utils import make_csv, INGIniousAdminPage


class CourseStudentListPage(INGIniousAdminPage):
    """ Course administration page: list of registered students """

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, __ = self.get_course_and_check_rights(courseid)
        return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, __ = self.get_course_and_check_rights(courseid, None, False)
        data = web.input()
        success_message = ""
        if "remove" in data:
            try:
                if data["type"] == "all":
                    aggregations = list(self.database.aggregations.find({"courseid": courseid}))
                    for aggregation in aggregations:
                        aggregation["students"] = []
                        for group in aggregation["groups"]:
                            group["students"] = []
                        self.database.aggregations.replace_one({"_id": aggregation["_id"]}, aggregation)
                else:
                    self.user_manager.course_unregister_user(course, data["username"])
                    success_message = _("User was successfully removed")
            except:
                pass
        elif "register" in data:
            if self.database.users.find_one({"username":data["username"].strip()}) is None:
                possible_user = self.database.users.find_one({"email":data["username"].strip()})
                if possible_user is None:
                    return self.page(course, error=_("Username nor email was not found with an already existing account in UNCode") )
                data["username"] = possible_user["username"]

            try:
                self.user_manager.course_register_user(course, data["username"].strip(), '', True)
                success_message = _("User was successfully added")
            except:
                return self.page(course, error = _("User could not be registered due to internal server error") )
        return self.page(course, success=success_message)

    def submission_url_generator(self, username):
        """ Generates a submission url """
        return "?format=taskid%2Fusername&users=" + username

    def page(self, course, error="", post=False, success=""):
        """ Get all data and display the page """
        users = sorted(list(self.user_manager.get_users_info(self.user_manager.get_course_registered_users(course, False)).items()),
                       key=lambda k: k[1][0] if k[1] is not None else "")

        users = OrderedDict(sorted(list(self.user_manager.get_users_info(course.get_staff()).items()),
                                   key=lambda k: k[1][0] if k[1] is not None else "") + users)

        user_data = OrderedDict([(username, {
            "username": username, "realname": user[0] if user is not None else "",
            "email": user[1] if user is not None else "", "total_tasks": 0,
            "task_grades": {"answer": 0, "match": 0}, "task_succeeded": 0, "task_tried": 0, "total_tries": 0,
            "grade": 0, "url": self.submission_url_generator(username)}) for username, user in users.items()])

        for username, data in self.user_manager.get_course_caches(list(users.keys()), course).items():
            user_data[username].update(data if data is not None else {})

        if "csv" in web.input():
            return make_csv(user_data)

        return self.template_helper.get_renderer().course_admin.student_list(course, list(user_data.values()), error, post, success)
