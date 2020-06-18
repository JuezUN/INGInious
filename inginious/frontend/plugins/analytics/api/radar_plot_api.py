import web
import datetime

from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


class RadarPlotAPI(SuperadminAPI):
    def API_GET(self):
        self.check_superadmin_rights()
        input_dict = web.input()
        username = input_dict.get('username', None)
        service = input_dict.get('service', None)
        start_date = input_dict.get('start_date', None)
        course_id = input_dict.get('course_id', None)

        # Generate query
        query_parameters = {}
        if username:
            query_parameters['username'] = username
        if service:
            query_parameters['service'] = service
        if course_id:
            query_parameters['course_id'] = course_id
        if start_date:
            start_date = datetime.datetime(*map(int, start_date.split('-')))
            query_parameters['date'] = {'$gte': start_date}

        data = {'services': [], 'visits': []}
        data_by_service = list(self.get_data_by_service(query_parameters))
        for val in data_by_service:
            data['services'].append(val['service'])
            data['visits'].append(val['visits'])
        return 200, data

    def get_data_by_service(self, filters):
        results = self.database.analytics.aggregate([
            {
                "$match": filters
            },
            {
                "$group": {
                    "_id": "$service",
                    "visits": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "_id": 1,
                }
            },
            {
                "$project": {"service": "$_id", "visits": 1, "_id": 0}
            }
        ])
        return results
