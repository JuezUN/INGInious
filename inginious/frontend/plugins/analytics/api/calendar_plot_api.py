import web

from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI
from ..utils import get_api_query_parameters


class CalendarPlotAPI(SuperadminAPI):
    def API_GET(self):
        self.check_superadmin_rights()
        input_dict = web.input()
        query_parameters = get_api_query_parameters(input_dict)

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
