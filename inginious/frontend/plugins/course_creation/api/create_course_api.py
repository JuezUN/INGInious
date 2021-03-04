import web

from inginious.frontend.plugins.utils import get_mandatory_parameter
import inginious.frontend.pages.api._api_page as api


class CreateCourseAPI(api.APIAuthenticatedPage):

    def _parse_and_validate_input(self):
        request_params = web.input()

        course_name = get_mandatory_parameter(request_params, "course_name")
        course_year = get_mandatory_parameter(request_params, "course_year")
        course_semester = get_mandatory_parameter(request_params, "course_semester")

        course_group = request_params.get("course_group", None)

        if not course_name:
            raise api.APIError(400, _("The course name cannot be empty."))

        if not course_year:
            raise api.APIError(400, _("The course year cannot be empty."))

        if not course_year.isnumeric():
            raise api.APIError(400, _("The course year must be a number."))

        if not course_semester:
            raise api.APIError(400, _("The course semester cannot be empty."))

        if not course_semester.isnumeric():
            raise api.APIError(400, _("The course semester must be a number."))

        if course_group and not course_group.isnumeric():
            raise api.APIError(400, _("The group must be a number."))

        return {"name": course_name, "group": course_group, "year": course_year, "semester": course_semester}

    def API_POST(self):
        try:
            data = self._parse_and_validate_input()
        except api.APIError as e:
            web.header('Content-Type', 'text/json; charset=utf-8')
            return e.status_code, {"status": "error", "text": e.return_value}

        if self.user_manager.user_is_superadmin():
            try:
                course_id, course_final_name = _generate_course_id_and_name(data["name"], data["group"], data["year"],
                                                                            data["semester"])

                self.course_factory.create_course(course_id, {"name": course_final_name, "accessible": False})
                web.header('Content-Type', 'text/json; charset=utf-8')
                return 200, {"status": "done", "course_page": "/admin/{}/settings".format(course_id)}
            except:
                web.header('Content-Type', 'text/json; charset=utf-8')
                return 400, {"status": "error", "text": _(
                    "Failed to create the course. It might either already exist or contain an invalid character (only alphanumeric in addition to '_' and '-' are accepted).")}


def _generate_course_id_and_name(name, group, year, semester):
    name_words = name.strip().split(" ")
    name_initials = "".join(map(lambda word: word.strip()[0].capitalize(), name_words))

    if len(name_words) > 1:
        final_id = name_initials
    else:
        final_id = name_words[0]

    final_name = name
    if group:
        final_id += "-Grupo{}".format(group)
        final_name += " - Grupo {}".format(group)

    final_id += "-{year}-{semester}".format(year=year, semester=semester)
    final_name += " - {year} - {semester}".format(year=year, semester=semester)

    return final_id, final_name
