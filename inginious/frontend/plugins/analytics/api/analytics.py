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

    def API_GET(self):
        self.check_superadmin_rights()
        input_dict = web.input()
        username = input_dict.get('username', None)
        service = input_dict.get('service', None)
        start_date = input_dict.get('start_date', None)
        course_id = input_dict.get('course_id', None)

        # Generate query
        consult_parameters = {}
        if username:
            consult_parameters['username'] = username
        if service:
            consult_parameters['service'] = service
        if course_id:
            consult_parameters['course_id'] = course_id
        if start_date:
            start_date = datetime.datetime(*map(int, start_date.split('-')))
            consult_parameters['date'] = {'$gte': start_date}

        results = []
        for result in self.database.analytics.find(consult_parameters):
            result['date'] = result['date'].isoformat()
            result['_id'] = str(result['_id'])
            results.append(result)
        return 200, results
