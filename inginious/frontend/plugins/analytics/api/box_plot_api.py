import web
import datetime

from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


class BoxPlotAPI(SuperadminAPI):
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

        services = {}
        data_by_service = list(self.get_data_by_service(query_parameters))
        for val in data_by_service:
            services[val['service']] = {}
            for date in val['dates']:
                services[val['service']][date['date']] = date['visits']

        all_dates = list(self.get_all_dates(query_parameters))
        all_dates = sorted(all_dates[-1]["all_dates"])

        services_names = services.keys()
        y_data = []
        for service in services_names:
            info = []
            for date in all_dates:
                if date in services[service]:
                    info.append(services[service][date])
                else:
                    info.append(0)
            y_data.append(info)

        results = {'x_data': list(services_names), "y_data": y_data}
        return 200, results

    def get_data_by_service(self, filters):
        results = self.database.analytics.aggregate([
            {
                "$match": filters
            },
            {
                "$group": {
                    "_id": {
                        "service": "$service",
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}}
                    },
                    "visits": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "_id.date": 1,
                }
            },
            {
                "$group": {
                    "_id": "$_id.service",
                    "dates": {
                        "$push": {
                            "date": "$_id.date",
                            "visits": "$visits"
                        },
                    },
                }
            },
            {
                "$project": {"service": "$_id", "dates": 1, "_id": 0}
            }
        ])
        return results

    def get_all_dates(self, filters):
        results = self.database.analytics.aggregate([
            {
                "$match": filters
            },
            {
                "$group": {
                    "_id": "null",
                    "all_dates": {"$addToSet": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}}},
                }
            },
            {
                "$project": {"_id": 0}
            },
        ])
        return results
