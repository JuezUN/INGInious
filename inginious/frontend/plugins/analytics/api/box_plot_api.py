import web

from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI
from ..utils import get_api_query_parameters


class BoxPlotAPI(SuperadminAPI):
    def API_GET(self):
        self.check_superadmin_rights()
        input_dict = web.input()
        query_parameters = get_api_query_parameters(input_dict)

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
                        "date": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$date"
                            }
                        }
                    },
                    "visits": {
                        "$sum": 1
                    }
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
                "$project": {
                    "service": "$_id",
                    "dates": 1,
                    "_id": 0
                }
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
