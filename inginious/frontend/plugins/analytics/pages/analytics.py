from inginious.common.course_factory import CourseFactory
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAuthPage
from ..analytics_collection_manager import AnalyticsCollectionManagerSingleton
from ..services_collection_manager import ServicesCollectionManagerSingleton
from ..utils import use_minified


class AnalyticsPage(SuperadminAuthPage):
    def GET_AUTH(self):
        self.check_superadmin_rights()

        self.template_helper.add_javascript(
            "https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        self.template_helper.add_javascript("https://d3js.org/d3.v3.min.js", position="header")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-latest.min.js", position="header")
        self.template_helper.add_javascript("https://unpkg.com/multiple-select@1.5.2/dist/multiple-select.min.js")
        self.template_helper.add_css("https://unpkg.com/multiple-select@1.5.2/dist/multiple-select.min.css")
        if use_minified():
            self.template_helper.add_javascript("/analytics/static/js/analytics.min.js")
            self.template_helper.add_css("/analytics/static/css/analytics.min.css")
        else:
            self.template_helper.add_javascript("/analytics/static/js/analytics.js")
            self.template_helper.add_javascript("/analytics/static/js/calendar_view.js")
            self.template_helper.add_javascript("/analytics/static/js/time_series.js")
            self.template_helper.add_javascript("/analytics/static/js/box_plot.js")
            self.template_helper.add_javascript("/analytics/static/js/radar.js")
            self.template_helper.add_javascript("/analytics/static/js/stacked_bar_plot.js")
            self.template_helper.add_css("/analytics/static/css/analytics.css")

        all_services = ServicesCollectionManagerSingleton.get_instance().get_all_services()
        return (
            self.template_helper
                .get_custom_renderer('frontend/plugins/analytics/pages')
                .analytics(services=all_services, all_courses=self.get_all_courses())
        )

    def get_all_courses(self):
        def get_course_name(course_id):
            if course_id:
                name = self.course_factory.get_course(course_id).get_name(
                    self.user_manager.session_language())
                return name if name else course_id
            else:
                return "No course"

        analytics_manager = AnalyticsCollectionManagerSingleton.get_instance()
        courses = analytics_manager.get_course_list()
        available_courses = sorted([{
            'id': course_id if course_id else "none",
            'name': get_course_name(course_id)
        } for course_id in courses], key=lambda x: x['name'])

        return available_courses
