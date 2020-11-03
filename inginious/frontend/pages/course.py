# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Course page """
import web

from inginious.frontend.pages.utils import INGIniousPage


class CoursePage(INGIniousPage):
    """ Course page """

    def get_course(self, courseid):
        """ Return the course """
        try:
            course = self.course_factory.get_course(courseid)
        except:
            raise web.notfound()

        return course

    def POST(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course = self.get_course(courseid)

        user_input = web.input()
        if "unregister" in user_input and course.allow_unregister():
            self.user_manager.course_unregister_user(course, self.user_manager.session_username())
            raise web.seeother(self.app.get_homepath() + '/mycourses')

        return self.show_page(course)

    def GET(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course = self.get_course(courseid)
        user_input = web.input()
        page = int(user_input.get("page", 1)) - 1
        tag = user_input.get("tag", "")
        return self.show_page(course, page, tag)

    def show_page(self, course, current_page=0, current_tag=""):
        """ Prepares and shows the course page """
        username = self.user_manager.session_username()
        if not self.user_manager.course_is_open_to_user(course, lti=False):
            return self.template_helper.get_renderer().course_unavailable()

        tasks = course.get_tasks()
        last_submissions = self.submission_manager.get_user_last_submissions(5, {"courseid": course.get_id(),
                                                                                 "taskid": {"$in": list(tasks.keys())}})

        for submission in last_submissions:
            submission["taskname"] = tasks[submission['taskid']].get_name(self.user_manager.session_language())

        tasks_data = {}
        user_tasks = self.database.user_tasks.find(
            {"username": username, "courseid": course.get_id(), "taskid": {"$in": list(tasks.keys())}})
        is_admin = self.user_manager.has_staff_rights_on_course(course, username)

        tasks_score = [0.0, 0.0]

        for taskid, task in tasks.items():
            tasks_data[taskid] = {"visible": task.get_accessible_time().after_start() or is_admin, "succeeded": False,
                                  "grade": 0.0}
            tasks_score[1] += task.get_grading_weight() if tasks_data[taskid]["visible"] else 0

        for user_task in user_tasks:
            tasks_data[user_task["taskid"]]["succeeded"] = user_task["succeeded"]
            tasks_data[user_task["taskid"]]["grade"] = user_task["grade"]

            weighted_score = user_task["grade"] * tasks[user_task["taskid"]].get_grading_weight()
            tasks_score[0] += weighted_score if tasks_data[user_task["taskid"]]["visible"] else 0

        course_grade = round(tasks_score[0] / tasks_score[1]) if tasks_score[1] > 0 else 0
        tag_list = course.get_all_tags_names_as_list(is_admin, self.user_manager.session_language())
        user_info = self.database.users.find_one({"username": username})

        # Filter tasks with the tag in case the tasks are filtered
        if not current_tag:
            filtered_tasks = tasks
        else:
            filtered_tasks = {task_id: task for task_id, task in tasks.items() if
                              current_tag in map(lambda x: x.get_name(), task.get_tags()[2] + task.get_tags()[0])}

        # Manage tasks pagination
        page_limit = 20
        total_tasks = len(filtered_tasks)
        pages = total_tasks // page_limit
        if (total_tasks % page_limit) != 0 or pages == 0:
            pages += 1
        if (page_limit * current_page + page_limit) < total_tasks:
            page_tasks_ids = list(filtered_tasks.keys())[page_limit * current_page:
                                                         page_limit * current_page + page_limit]
        else:
            page_tasks_ids = list(filtered_tasks.keys())[page_limit * current_page:]

        filtered_tasks = {task_id: tasks_data[task_id] for task_id, __ in filtered_tasks.items() if
                          task_id in page_tasks_ids}

        return self.template_helper.get_renderer().course(user_info, course, last_submissions, tasks,
                                                          filtered_tasks, course_grade, tag_list, pages,
                                                          current_page + 1, current_tag)
