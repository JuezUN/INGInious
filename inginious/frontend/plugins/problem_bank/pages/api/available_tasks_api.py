import web

from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.utils.admin_api import AdminApi


class AvailableTasksApi(AdminApi):

    def API_GET(self):
        parameters = web.input()
        limit = int(get_mandatory_parameter(parameters, "limit"))
        page = int(get_mandatory_parameter(parameters, "page"))

        course_ids = set(bank["courseid"]
                         for bank in self.database.problem_banks.find())

        all_courses = self.course_factory.get_all_courses()
        for course_id, course in all_courses.items():
            if self.user_manager.has_admin_rights_on_course(course):
                course_ids.add(course_id)

        course_ids = list(course_ids)

        tasks = list(self.database.tasks_cache.aggregate([
            {
                "$match": {
                    "course_id": {"$in": course_ids}
                }
            },
            {
                "$project": {
                    "course_id": 1,
                    "task_id": 1,
                    "task_name": 1,
                    "task_author": 1,
                    "task_context": 1,
                    "tags": 1,
                    "course_name": 1,
                    "_id": 0,
                }
            },
            {
                "$sort": {"task_name": 1}
            }
        ]))

        left = limit * (page - 1)
        right = left + limit
        total_pages = len(tasks) // limit
        if len(tasks) % limit != 0 or total_pages == 0:
            total_pages += 1

        if right >= len(tasks):
            tasks = tasks[left:]
        else:
            tasks = tasks[left:right]

        response = {'total_pages': total_pages, "tasks": tasks}
        return 200, response
