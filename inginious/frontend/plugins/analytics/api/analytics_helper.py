import web
import datetime
import json
from collections import OrderedDict
import inginious.frontend.pages.api._api_page as api
from inginious.frontend.pages.api._api_page import APIAuthenticatedPage
from inginious.frontend.plugins.analytics.manager import AnalyticsManager


class AnalyticsHelperAPI(APIAuthenticatedPage):
    def API_GET(self):
        manager = AnalyticsManager(self.database)

        username = web.input(username=None).username
        service = web.input(service=None).service
        
        session_id = self.user_manager.session_id()
        date = datetime.datetime.now()


        print(manager.add_visit(service, username, date, session_id))
        
        return 200, ""