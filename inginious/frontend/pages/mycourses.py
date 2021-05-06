# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Index page """
from collections import OrderedDict
import re
import textdistance
import web

from inginious.frontend.pages.utils import INGIniousAuthPage


class MyCoursesPage(INGIniousAuthPage):
    """ Index page """

    def GET_AUTH(self):  # pylint: disable=arguments-differ
        """ Display main course list page """
        user_input = web.input()
        page = int(user_input.get("page", 1) or 1) - 1
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

    def filter_courses(self, courses, query):
        """
        Filter the courses with respect the query. First, the course names and query are tokenized, removing
        spaces, hyphens, and punctuation characters. Then, a score is obtained comparing each token of the
        query with each course name, this is using the algorithm jaro-winkler, to calculate the distance
        between two tokens. A list of tasks is obtained, and a task with a score of more or equal 0.9, is
        appended. The resulting courses are sorted with respect the obtained score.
         """
        if query == "":
            return courses

        filtered_courses = []
        for course in courses.values():
            course_name = course.get_name(self.user_manager.session_language())
            course_tokens = re.findall(r"[\w']+", course_name.lower())
            query_tokens = re.findall(r"[\w']+", query.lower())
            total_distance = 0
            can_insert = False
            for course_name_token in course_tokens:
                for query_token in query_tokens:
                    dist = textdistance.jaro_winkler(course_name_token, query_token)
                    if dist >= 0.8:
                        # Only distance values with >= 0.8 are taken into account to calculate the score
                        # In case the distance is equal to 1, the weight is double for equal tokens.
                        if dist == 1:
                            dist *= 2
                        total_distance += dist
                        can_insert = True
            if total_distance >= 0.9 and can_insert:
                filtered_courses.append((course, total_distance))
        return OrderedDict(map(lambda x: (x[0].get_id(), x[0]), sorted(filtered_courses, key=lambda x: -x[1])))

    def show_page(self, success, current_page=0, query=""):
        """  Display main course list page """
        username = self.user_manager.session_username()
        user_info = self.database.users.find_one({"username": username})

        all_courses = self.course_factory.get_all_courses()

        # Display
        open_courses = {courseid: course for courseid, course in all_courses.items()
                        if self.user_manager.course_is_open_to_user(course, username, None) and
                        self.user_manager.course_is_user_registered(course, username)}
        open_courses = OrderedDict(sorted(iter(open_courses.items()),
                                          key=lambda x: x[1].get_name(self.user_manager.session_language())))

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
        open_courses = self.filter_courses(open_courses, query)

        # Manage courses pagination
        page_limit = 20
        total_open_courses = len(open_courses)
        pages = total_open_courses // page_limit
        if (total_open_courses % page_limit) != 0 or pages == 0:
            pages += 1

        if (page_limit * current_page + page_limit) < total_open_courses:
            page_courses = list(open_courses.values())[page_limit * current_page:
                                                       page_limit * current_page + page_limit]
        else:
            page_courses = list(open_courses.values())[page_limit * current_page:]

        filtered_open_courses = OrderedDict(list(map(lambda x: (x.get_id(), x), page_courses)))

        return self.template_helper.get_renderer().mycourses(filtered_open_courses, registerable_courses,
                                                             except_free_last_submissions, success, pages,
                                                             current_page + 1, query)
