import web
import json

from os.path import dirname, join
from collections import OrderedDict

from inginious.frontend.plugins.utils.admin_api import AdminApi
from inginious.frontend.plugins.utils import get_mandatory_parameter
from ...constants import CUSTOM_RUBRIC_FILENAME

_static_folder_path = join(dirname(dirname(dirname(__file__))), "static")


class UploadCustomRubric(AdminApi):
    def API_POST(self):
        """
        Method receiving POST request, receiving the file and course to upload a custom rubric for the course.
        """
        # TODO: What if another (uploaded or the default) rubric was already used to add custom rubrics?
        file = get_mandatory_parameter(web.input(), "file")
        course_id = get_mandatory_parameter(web.input(), "course")

        course = self._get_course_and_check_rights(course_id)
        if course is None:
            return 200, {"status": "error",
                         "text": _("The course does not exist or the user does not have permissions.")}

        try:
            text = file.decode("utf-8")
        except:
            return 200, {"status": "error", "text": _("The file is not coded in UTF-8. Please change the encoding.")}

        try:
            rubric = json.loads(text, object_pairs_hook=OrderedDict)
        except:
            return 200, {"status": "error",
                         "text": _("The JSON format is not correct. Please check the file and upload it again.")}

        try:
            parsed_rubric = self._parse_rubric(rubric)
        except Exception as e:
            return 200, {"status": "error", "text": str(e)}

        course_fs = self.course_factory.get_course_fs(course_id)
        course_fs.put(CUSTOM_RUBRIC_FILENAME, json.dumps(parsed_rubric))

        message = _("The rubric was successfully uploaded. Refresh the page to load the changes.")

        return 200, {"status": "success", "text": message}

    def _parse_rubric(self, rubric):
        if not len(rubric) or not rubric:
            raise Exception(_("The uploaded rubric is empty."))

        column_names = list(rubric.keys())
        categories = sorted(list(rubric[column_names[0]]))

        if not (len(column_names) or len(categories)):
            raise Exception(_("The rubric is not well formatted."))

        parsed_rubric = OrderedDict()

        for column_name in column_names:
            categories_column = rubric[column_name].keys()
            if not categories_column or len(categories_column) != len(categories):
                raise Exception(_("There are some missing rows."))
            if sorted(list(categories_column)) != categories:
                raise Exception(_("Not all rows have the same name."))

            for value_cell in rubric[column_name].values():
                if not value_cell:
                    raise Exception(_("The values of the cells cannot be empty."))

            parsed_rubric[column_name] = OrderedDict(sorted(rubric[column_name].items()))

        return parsed_rubric

    def _get_course_and_check_rights(self, course_id):
        """Retrieves the course, checks it exists and has admin rights on the course."""
        try:
            course = self.course_factory.get_course(course_id)
        except:
            return None

        if not self.user_manager.has_admin_rights_on_course(course):
            return None

        return course
