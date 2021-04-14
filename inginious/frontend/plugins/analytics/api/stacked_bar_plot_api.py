import web

from inginious.frontend.pages.api._api_page import APIError
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI
from ..utils import get_api_query_parameters


def get_course_names(data):
    return list(map(lambda course: course["course"], data))


def create_y_data_list(num_courses, num_services):
    return [[0] * num_services for i in range(num_courses)]


def get_visit_values(data, num_course, service_names):
    y_data_list = create_y_data_list(num_course, len(service_names))
    for i in range(len(data)):
        course = data[i]
        for service in course["data"]:
            index = service_names.index(service["service"])
            y_data_list[i][index] = service["visits"]
    return y_data_list


class StackedBarPlotAPI(SuperadminAPI):
    def API_GET(self):
        self.check_superadmin_rights()
        input_dict = web.input()

        try:
            query_parameters = get_api_query_parameters(input_dict)
        except APIError as error:
            return error.status_code, {"error": error.return_value}

        data = list(self.get_visits_data(query_parameters))

        course_names = get_course_names(data)
        service_names = self.get_service_names(query_parameters)

        visits = get_visit_values(data, len(course_names), service_names)

        results = {"x_data": course_names, "y_data": visits, "services": service_names}

        return 200, results

    def get_visits_data(self, filters):
        results = self.database.analytics.aggregate([
            {
                "$match": filters
            },
            {
                "$group": {
                    "_id": {
                        "service": "$service",
                        "course_id": "$course_id",

                    },
                    "visits": {
                        "$sum": 1
                    }
                }
            },
            {
                "$group": {
                    "_id": "$_id.course_id",
                    "data": {
                        "$push": {
                            "service": "$_id.service",
                            "visits": "$visits"
                        }
                    }
                }
            },
            {
                "$project": {
                    "course": "$_id",
                    "data": 1,
                    "_id": 0
                }
            },
            {
                "$sort": {
                    "course": 1
                }
            }
        ])
        return results

    def get_service_names(self, filters):
        results = self.database.analytics.aggregate([
            {
                "$match": filters
            },
            {
                "$group": {
                    "_id": "$service"
                }
            },
            {
                "$project": {
                    "service": "$_id",
                    "_id": 0
                }
            }
        ])
        service_ids = sorted(list(map(lambda service_id: service_id["service"], results)))
        return service_ids
