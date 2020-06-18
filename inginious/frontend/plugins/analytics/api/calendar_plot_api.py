import web
import datetime

from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


class CalendarPlotAPI(SuperadminAPI):
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

        results = {}
        data = self.get_data(query_parameters)
        data = list(data)
        for val in data:
            results[val['date']] = val['count']
        return 200, results

    def get_data(self, filters):
        results = self.database.analytics.aggregate([
            {
                "$match": filters
            },
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                    "count": {"$sum": 1},
                }
            },
            {
                "$project": {"date": "$_id", "count": 1, "_id": 0}
            }
        ])
        return results
