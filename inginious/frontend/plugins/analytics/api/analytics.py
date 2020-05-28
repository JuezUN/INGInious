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
        username = web.input(username=None).username
        service = web.input(service=None).service
        start_date = web.input(start_date=None).start_date
        end_date = web.input(end_date=None).end_date
        courseid = web.input(courseid=None).courseid
        service_type = web.input(service_type=None).service_type

        # Do all the consult
        consult_parameters = {}
        users = OrderedDict()
        if username:
            consult_parameters['username'] = username
        if service:
            consult_parameters['service'] = service
        if start_date and end_date:
            start_date = datetime.datetime(*map(int, start_date.split('-')))
            end_date = datetime.datetime(*map(int, end_date.split('-')))
            consult_parameters['date'] = {'$gte': start_date, '$lt': end_date}
        if service_type:
            consult_parameters['service_type'] = service_type
        if courseid is not None:
            course = self.course_factory.get_course(courseid)
            users = sorted(list(
                self.user_manager.get_users_info(self.user_manager.get_course_registered_users(course, False)).items()),
                key=lambda k: k[1][0] if k[1] is not None else "")

            users = OrderedDict(sorted(list(self.user_manager.get_users_info(course.get_staff()).items()),
                                       key=lambda k: k[1][0] if k[1] is not None else "") + users)

        results = []
        for result in self.database.analytics.find(consult_parameters):
            result['date'] = result['date'].isoformat()
            result['_id'] = str(result['_id'])
            if courseid is not None:
                if result['username'] in users:
                    results.append(result)
            else:
                results.append(result)
        return 200, results
