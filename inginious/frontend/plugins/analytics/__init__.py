import os

from inginious.frontend.plugins.utils import create_static_resource_page
from .pages.analytics import AnalyticsPage
from .api.analytics import AnalyticsAPI
from .api.calendar_plot_api import CalendarPlotAPI
from .api.time_series_plot_api import TimeSeriesPlotAPI
from .api.box_plot_api import BoxPlotAPI
from .api.radar_plot_api import RadarPlotAPI
from .utils import set_use_minified
from .services_collection_manager import ServicesCollectionManagerSingleton
from .analytics_collection_manager import AnalyticsCollectionManagerSingleton

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, course_factory, client, plugin_config):
    plugin_manager.add_page(r'/analytics/static/(.*)', create_static_resource_page(_static_folder_path))
    plugin_manager.add_page('/analytics/', AnalyticsPage)
    plugin_manager.add_page('/api/analytics/', AnalyticsAPI)
    plugin_manager.add_page('/api/calendar_plot_analytics/', CalendarPlotAPI)
    plugin_manager.add_page('/api/time_series_plot_analytics/', TimeSeriesPlotAPI)
    plugin_manager.add_page('/api/box_plot_analytics/', BoxPlotAPI)
    plugin_manager.add_page('/api/radar_plot_analytics/', RadarPlotAPI)

    set_use_minified(plugin_config.get("use_minified", True))

    def analytics_hook():
        if plugin_manager.get_user_manager().user_is_superadmin():
            return _(""""<li><a href='/analytics/' class='navbar-link'>
            <i class='fa fa-bar-chart fa-fw'></i> Analytics</a></li>""")

    plugin_manager.add_hook("superadmin_options", lambda: analytics_hook())

    ServicesCollectionManagerSingleton(plugin_manager.get_database())
    AnalyticsCollectionManagerSingleton(plugin_manager.get_database())
