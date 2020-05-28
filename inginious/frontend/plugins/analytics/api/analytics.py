import web
import datetime
from collections import OrderedDict

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
            analytics_manager.add_visit(service, username, date, session_id)
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

        # Do all the consult
        consult_parameters = {}
        users = OrderedDict()
        if username:
            consult_parameters['username'] = username
        if service:
            consult_parameters['service'] = service
        if start_date:
            start_date = datetime.datetime(*map(int, start_date.split('-')))
            consult_parameters['date'] = {'$gte': start_date}
        # if courseid is not None:
        #     course = self.course_factory.get_course(courseid)
        #     users = sorted(list(
        #         self.user_manager.get_users_info(self.user_manager.get_course_registered_users(course, False)).items()),
        #         key=lambda k: k[1][0] if k[1] is not None else "")
        #
        #     users = OrderedDict(sorted(list(self.user_manager.get_users_info(course.get_staff()).items()),
        #                                key=lambda k: k[1][0] if k[1] is not None else "") + users)

        results = []
        for result in self.database.analytics.find(consult_parameters):
            result['date'] = result['date'].isoformat()
            result['_id'] = str(result['_id'])
            if result['username'] in users:
                    results.append(result)
            else:
                results.append(result)
        return 200, results
