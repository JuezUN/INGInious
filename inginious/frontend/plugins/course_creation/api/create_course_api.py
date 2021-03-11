# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import uuid
import web

from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.common.exceptions import InvalidNameException, CourseAlreadyExistsException
import inginious.frontend.pages.api._api_page as api


class CreateCourseAPI(api.APIAuthenticatedPage):
    """ API to create a course from the Course Creation Modal. """

    def _parse_and_validate_input(self):
        request_params = web.input()

        course_name = get_mandatory_parameter(request_params, "course_name")
        course_year = get_mandatory_parameter(request_params, "course_year")
        course_semester = get_mandatory_parameter(request_params, "course_semester")

        course_group = request_params.get("course_group", None)
        course_to_copy_id = request_params.get("course_to_copy_id", None)

        if not course_name:
            raise api.APIError(400, _("The course name cannot be empty."))

        if not course_year:
            raise api.APIError(400, _("The year field cannot be empty."))

        if not course_year.isnumeric():
            raise api.APIError(400, _("The year must be a number."))

        if not course_semester:
            raise api.APIError(400, _("The semester field cannot be empty."))

        if not course_semester.isnumeric():
            raise api.APIError(400, _("The semester must be a number."))

        if course_group and not course_group.isnumeric():
            raise api.APIError(400, _("The group must be a number."))

        data = {"name": course_name, "group": course_group, "year": course_year, "semester": course_semester}

        all_courses = set(self.course_factory.get_all_courses().keys())
        if course_to_copy_id and course_to_copy_id != "-1":
            if course_to_copy_id not in all_courses:
                raise api.APIError(400, _("The selected course to copy tasks from does not exist."))

            data["course_to_copy"] = course_to_copy_id

        return data

    def _copy_tasks(self, source_course_id, target_course_id):
        source_course = self.course_factory.get_course(source_course_id)
        source_tasks = self.task_factory.get_all_tasks(source_course)

        target_fs = self.course_factory.get_course_fs(target_course_id)

        copied_tasks_target_course = set()

        for source_task in source_tasks.values():
            new_task_id = _generate_new_task_id(copied_tasks_target_course)
            try:
                target_fs.copy_to(source_task.get_fs().prefix, new_task_id)
                copied_tasks_target_course.add(new_task_id)
            except:
                return True
        return False

    def API_POST(self):
        try:
            data = self._parse_and_validate_input()
        except api.APIError as exception:
            web.header("Content-Type", "text/json; charset=utf-8")
            return exception.status_code, {"status": "error", "text": exception.return_value}

        if self.user_manager.user_is_superadmin():
            try:
                course_id, course_final_name = _generate_course_id_and_name(data["name"], data["group"], data["year"],
                                                                            data["semester"])

                self.course_factory.create_course(course_id, {"name": course_final_name, "accessible": False})

                if "course_to_copy" in data:
                    # Copy tasks in case a course was selected
                    clone_failed = self._copy_tasks(data["course_to_copy"], course_id)
                    if clone_failed:
                        web.header("Content-Type", "text/json; charset=utf-8")
                        return 500, {"status": "error", "text": _("An internal error occurred while copying tasks.")}

                web.header("Content-Type", "text/json; charset=utf-8")
                return 200, {
                    "status": "done",
                    "course_page": "/admin/{}/settings".format(course_id),
                    "text": _("The course was successfully created.")
                }
            except InvalidNameException:
                web.header("Content-Type", "text/json; charset=utf-8")
                return 400, {"status": "error", "text": _(
                    "The text may contain an invalid character. Only alphanumeric characters, in addition to '_' and '-' are accepted.")}
            except CourseAlreadyExistsException:
                web.header("Content-Type", "text/json; charset=utf-8")
                return 400, {"status": "error", "text": _(
                    "A course with the id {} already exists.".format(course_id))}
            except Exception:
                web.header("Content-Type", "text/json; charset=utf-8")
                return 400, {"status": "error", "text": _("An error occurred while creating the course")}


def _generate_course_id_and_name(name, group, year, semester):
    """ Generate the new course id and name taking into account the inserted data. """
    name_words = name.strip().split(" ")

    # If the number of words is greater than 1, the final ID will have the capitalized initials of each word in the
    # name. Otherwise, the final name is the given name by the user.
    if len(name_words) > 1:
        # Get the capitalized initials for each word in the name
        name_initials = "".join(map(lambda word: word.strip()[0].capitalize(), name_words))
        new_course_id = name_initials
    else:
        new_course_id = name.strip()

    new_course_name = name.strip()
    if group:
        new_course_id += "-Group{}".format(group)
        new_course_name += " | Grupo {}".format(group)

    new_course_id += "-{year}-{semester}".format(year=year, semester=semester)
    new_course_name += " | {year} - {semester}".format(year=year, semester=semester)

    return new_course_id, new_course_name


def _generate_new_task_id(target_course_tasks):
    """ Generate an uuid for the new task to be copied. """
    copy_id = str(uuid.uuid4())
    while copy_id in target_course_tasks:
        copy_id = str(uuid.uuid4())
    return copy_id
