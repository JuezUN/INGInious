import datetime
from inginious.frontend.pages.utils import INGIniousAuthPage
from inginious.frontend.plugins.analytics.manager import AnalyticsManager

class AnalyticsPage(INGIniousAuthPage):
    def GET_AUTH(self):

        return (
            self.template_helper
            .get_custom_renderer('frontend/plugins/analytics/pages')
            .dashboard()
        )