import datetime
from inginious.frontend.pages.utils import INGIniousAuthPage
from inginious.frontend.plugins.analytics.analytics_collection_manager import AnalyticsCollectionManager
from .constants import base_renderer_path, get_use_minified

class UserStatisticsPage(INGIniousAuthPage):
    def GET_AUTH(self, course_id):
        analytics_collection_manager = AnalyticsCollectionManager(self.database)
        analytics_params = {
            'username': self.user_manager.session_username(),
            'service': 'statistics',
            'date': datetime.datetime.now(),
            'session_id': self.user_manager.session_id()
        }
        analytics_collection_manager.add_visit(**analytics_params)

        self.template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-1.30.0.min.js")
        if get_use_minified():
            self.template_helper.add_javascript("/statistics/static/js/user_statistics.min.js")
            self.template_helper.add_css("/statistics/static/css/statistics.min.css")
        else:
            self.template_helper.add_javascript("/statistics/static/js/statistics.js")
            self.template_helper.add_javascript("/statistics/static/js/user_statistics.js")
            self.template_helper.add_css("/statistics/static/css/statistics.css")

        return (
            self.template_helper
            .get_custom_renderer(base_renderer_path())
            .user_statistics(course_id)
        )


def statistics_course_menu_hook(course, template_helper):
    return """
            <h3>Statistics</h3>
            <a class="list-group-item list-group-item-info"
                href="/user_statistics/{course_id}">
                <i class="fa fa-group fa-fw"></i>
                My Statistics
            </a>""".format(course_id=course.get_id())
        