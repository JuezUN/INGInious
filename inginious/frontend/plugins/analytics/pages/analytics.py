from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAuthPage
from ..services_collection_manager import ServicesCollectionManagerSingleton
from ..utils import use_minified


class AnalyticsPage(SuperadminAuthPage):
    def GET_AUTH(self):
        self.check_superadmin_rights()

        self.template_helper.add_javascript("https://d3js.org/d3.v3.min.js", position="header")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-latest.min.js", position="header")

        if use_minified():
            self.template_helper.add_javascript("/analytics/static/analytics.min.js")
            self.template_helper.add_css("/analytics/static/analytics.min.css")

        else:
            self.template_helper.add_javascript("/analytics/static/analytics.js")
            self.template_helper.add_javascript("/analytics/static/calendar_view.js")
            self.template_helper.add_javascript("/analytics/static/time_series.js")
            self.template_helper.add_javascript("/analytics/static/box_plot.js")
            self.template_helper.add_javascript("/analytics/static/radar.js")
            self.template_helper.add_css("/analytics/static/dashboard.css")

        all_services = ServicesCollectionManagerSingleton.get_instance().get_all_services()
        return (
            self.template_helper
                .get_custom_renderer('frontend/plugins/analytics/pages')
                .dashboard(services=all_services)
        )
