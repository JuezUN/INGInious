import web
import datetime

from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI
from ..analytics_collection_manager import AnalyticsCollectionManagerSingleton
from ..services_collection_manager import ServicesCollectionManagerSingleton


class AnalyticsAPI(SuperadminAPI):
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
