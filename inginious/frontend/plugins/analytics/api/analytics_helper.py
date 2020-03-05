import web
import datetime

from inginious.frontend.pages.api._api_page import APIAuthenticatedPage
from ..analytics_collection_manager import AnalyticsCollectionManager


class AnalyticsHelperAPI(APIAuthenticatedPage):
    def API_GET(self):
        manager = AnalyticsCollectionManager(self.database)

        username = self.user_manager.session_username()
        service = web.input(service=None).service

        session_id = self.user_manager.session_id()
        date = datetime.datetime.now()
        manager.add_visit(service, username, date, session_id)
        return 200, ""
