import web

from inginious.frontend.plugins.utils.admin_api import AdminApi
from inginious.frontend.plugins.utils import get_mandatory_parameter


class FilterTasksApi(AdminApi):

    def API_POST(self):

        parameters = web.input()
        task_query = get_mandatory_parameter(parameters, "task_query")
        limit = int(get_mandatory_parameter(parameters, "limit"))
        page = int(get_mandatory_parameter(parameters, "page"))

        course_ids = set(bank["courseid"]
                         for bank in self.database.problem_banks.find())

        for course_id, course in self.course_factory.get_all_courses().items():
            if self.user_manager.has_admin_rights_on_course(course):
                course_ids.add(course_id)

        tasks = []
        result_tasks = self.database.tasks_cache.aggregate([
            {
                "$match":
                    {
                        "$text": {
                            "$search": task_query,
                        }
                    }
            },
            {
                "$match":
                    {
                        "course_id": {"$in": list(course_ids)}
                    }
            },
        ])

        for task in result_tasks:
            dict_task = {"course_id": task["course_id"], "task_id": task["task_id"], "task_name": task["task_name"],
                         "task_author": task["task_author"], "task_context": task["task_context"],
                         "tags": task.get("tags", []), "course_name": task["course_name"]
                         }
            tasks.append(dict_task)

        left = limit * (page - 1)
        right = left + limit
        tasks = list(sorted(tasks, key=lambda k: (k['course_name'], k['task_name'])))
        total_pages = len(tasks) // limit
        if len(tasks) % limit != 0 or total_pages == 0:
            total_pages += 1

        if right >= len(tasks):
            tasks = tasks[left:]
        else:
            tasks = tasks[left:right]

        response = {'total_pages': total_pages, "tasks": tasks}
        return 200, response
