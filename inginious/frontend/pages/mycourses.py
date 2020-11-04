# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Index page """
from collections import OrderedDict
import re
import web

from inginious.frontend.pages.utils import INGIniousAuthPage


class MyCoursesPage(INGIniousAuthPage):
    """ Index page """

    def GET_AUTH(self):  # pylint: disable=arguments-differ
        """ Display main course list page """
        user_input = web.input()
        page = int(user_input.get("page", 1)) - 1
        query = user_input.get("query", "")
        return self.show_page(None, page, query)

    def POST_AUTH(self):  # pylint: disable=arguments-differ
        """ Parse course registration or course creation and display the course list page """

        username = self.user_manager.session_username()
        user_info = self.database.users.find_one({"username": username})
        user_input = web.input()
        success = None

        # Handle registration to a course
        if "register_courseid" in user_input and user_input["register_courseid"] != "":
            try:
                course = self.course_factory.get_course(user_input["register_courseid"])
                if not course.is_registration_possible(user_info):
                    success = False
                else:
                    success = self.user_manager.course_register_user(course, username,
                                                                     user_input.get("register_password", None))
            except:
                success = False
        elif "new_courseid" in user_input and self.user_manager.user_is_superadmin():
            try:
                courseid = user_input["new_courseid"]
                self.course_factory.create_course(courseid, {"name": courseid, "accessible": False})
                success = True
            except:
                success = False

        return self.show_page(success)

    def show_page(self, success, current_page=0, query=""):
        """  Display main course list page """
        username = self.user_manager.session_username()
        user_info = self.database.users.find_one({"username": username})

        all_courses = self.course_factory.get_all_courses()

        # Display
        open_courses = {courseid: course for courseid, course in all_courses.items()
                        if self.user_manager.course_is_open_to_user(course, username, None) and
                        self.user_manager.course_is_user_registered(course, username)}

        last_submissions = self.submission_manager.get_user_last_submissions(5, {
            "courseid": {"$in": list(open_courses.keys())}})
        except_free_last_submissions = []
        for submission in last_submissions:
            try:
                submission["task"] = open_courses[submission['courseid']].get_task(submission['taskid'])
                except_free_last_submissions.append(submission)
            except:
                pass

        registerable_courses = {courseid: course for courseid, course in all_courses.items() if
                                not self.user_manager.course_is_user_registered(course, username) and
                                course.is_registration_possible(user_info)}

        registerable_courses = OrderedDict(sorted(iter(registerable_courses.items()),
                                                  key=lambda x: x[1].get_name(self.user_manager.session_language())))

        # Filter open courses
        if query == "":
            regex_query = r".*"
        else:
            regex_query = r".*{}.*".format(query)
        open_courses = {course_id: course for course_id, course in open_courses.items() if
                        re.match(regex_query, course.get_name(self.user_manager.session_language()), re.IGNORECASE)}

        # Manage courses pagination
        page_limit = 20
        total_open_courses = len(open_courses)
        pages = total_open_courses // page_limit
        if (total_open_courses % page_limit) != 0 or pages == 0:
            pages += 1

        if (page_limit * current_page + page_limit) < total_open_courses:
            page_courses_ids = list(open_courses.keys())[page_limit * current_page:
                                                         page_limit * current_page + page_limit]
        else:
            page_courses_ids = list(open_courses.keys())[page_limit * current_page:]

        filtered_open_courses = {course_id: open_courses[course_id] for course_id, __ in open_courses.items() if
                                 course_id in page_courses_ids}
        filtered_open_courses = OrderedDict(
            sorted(iter(filtered_open_courses.items()),
                   key=lambda x: x[1].get_name(self.user_manager.session_language())))

        return self.template_helper.get_renderer().mycourses(filtered_open_courses, registerable_courses,
                                                             except_free_last_submissions, success, pages,
                                                             current_page + 1, query)
