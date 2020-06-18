import web

from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI
from ..utils import get_api_query_parameters


class RadarPlotAPI(SuperadminAPI):
    def API_GET(self):
        self.check_superadmin_rights()
        input_dict = web.input()
        query_parameters = get_api_query_parameters(input_dict)

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
