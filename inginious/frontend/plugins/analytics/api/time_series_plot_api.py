import web

from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI
from ..utils import get_api_query_parameters


class TimeSeriesPlotAPI(SuperadminAPI):
    def API_GET(self):
        self.check_superadmin_rights()
        input_dict = web.input()
        query_parameters = get_api_query_parameters(input_dict)

        results = {'data_by_service': {}, 'data_all_services': {}}
        data_by_service = list(self.get_data_by_service(query_parameters))
        for val in data_by_service:
            results['data_by_service'][val['service']] = val['dates']

        data_by_date = list(self.get_data_by_date(query_parameters))
        results['data_all_services']['dates'] = []
        results['data_all_services']['counts'] = []
        for val in data_by_date:
            results['data_all_services']['dates'].append(val['date'])
            results['data_all_services']['counts'].append(val['counts'])
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

    def get_data_by_date(self, filters):
        results = self.database.analytics.aggregate([
            {
                "$match": filters
            },
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                    "counts": {"$sum": 1},
                }
            },
            {
                "$sort": {
                    "_id": 1,
                }
            },
            {
                "$project": {"date": "$_id", "counts": 1, "_id": 0}
            }
        ])
        return results
