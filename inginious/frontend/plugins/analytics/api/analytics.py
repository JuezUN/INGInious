import web
import datetime

from inginious.frontend.pages.api._api_page import APIError
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI
from ..analytics_collection_manager import AnalyticsCollectionManagerSingleton
from ..services_collection_manager import ServicesCollectionManagerSingleton
from ..utils import get_api_query_parameters


class AnalyticsAPI(SuperadminAPI):
    def API_GET(self):
        self.check_superadmin_rights()
        input_dict = web.input()
        try:
            query_parameters = get_api_query_parameters(input_dict)
        except APIError as error:
            return error.status_code, {"error": error.return_value}
        data_to_send = self.get_data_to_send(query_parameters)
        return 200, data_to_send

    def API_POST(self):
        analytics_manager = AnalyticsCollectionManagerSingleton.get_instance()
        services_manager = ServicesCollectionManagerSingleton.get_instance()

        username = self.user_manager.session_username()
        session_id = self.user_manager.session_id()
        date = datetime.datetime.now()
        try:
            input_dict = web.input()
            service = {
                "key": input_dict.get("service[key]", None),
                "name": input_dict.get("service[name]", None)
            }
            course_id = input_dict.get("course_id", None)
            analytics_manager.add_visit(service, username, date, session_id, course_id)
            services_manager.add_service(service)
            return 200, ""
        except:
            return 400, "Bad Request."

    def get_analytics_data(self, filters):
        results = self.database.analytics.aggregate([
            {
                "$match": filters
            },
            {
                "$project": {
                    "username": 1,
                    "service": 1,
                    "date": 1,
                    "course_id": 1
                }
            }
        ])
        return results

    def get_data_to_send(self, filters):
        analytics_data = self.get_analytics_data(filters)
        data = []
        all_services = dict(ServicesCollectionManagerSingleton.get_instance().get_all_services())

        for analytic in analytics_data:
            analytic_info = {
                "_id": str(analytic["_id"]),
                "course_id": analytic["course_id"],
                "course": self.course_factory.get_course(analytic["course_id"]).get_name(
                    self.user_manager.session_language()),
                "service_id": analytic["service"],
                "service": all_services[analytic["service"]],
                "username": analytic["username"],
                "date": analytic["date"].strftime("%d/%m/%Y, %H:%M:%S")
            }
            data.append(analytic_info)
        return data
