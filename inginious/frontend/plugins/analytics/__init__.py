import os
from inginious.frontend.plugins.utils import create_static_resource_page

from .pages.dashboard import AnalyticsPage
from .api.analytics_consults import AnalyticsConsultAPI
from .api.analytics_helper import AnalyticsHelperAPI

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, course_factory, client, config):
    plugin_manager.add_page(r'/analytics/static/(.*)', create_static_resource_page(_static_folder_path))
    plugin_manager.add_page('/analytics/', AnalyticsPage)
    plugin_manager.add_page('/api/analytics_consult/', AnalyticsConsultAPI)
    plugin_manager.add_page('/api/analytics_helper/', AnalyticsHelperAPI)
