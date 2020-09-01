from inginious.frontend.pages.utils import INGIniousAuthPage
from .constants import base_renderer_path, get_use_minified


class UserStatisticsPage(INGIniousAuthPage):
    def GET_AUTH(self, course_id):

        self.template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-latest.min.js")
        if get_use_minified():
            self.template_helper.add_javascript("/statistics/static/js/user_statistics.min.js")
            self.template_helper.add_css("/statistics/static/css/statistics.min.css")
        else:
            self.template_helper.add_javascript("/statistics/static/js/statistics.js")
            self.template_helper.add_javascript("/statistics/static/js/user_statistics.js")
            self.template_helper.add_css("/statistics/static/css/statistics.css")

        course = self.course_factory.get_course(course_id)
        return (
            self.template_helper
                .get_custom_renderer(base_renderer_path())
                .user_statistics(course)
        )


def statistics_course_menu_hook(course, template_helper):
    statistics_str = _("Statistics")
    my_statistics_str = _("My statistics")
    return """
            <h3>{statistics_str}</h3>
            <a class="list-group-item list-group-item-info"
                href="/user_statistics/{course_id}">
                <i class="fa fa-group fa-fw"></i>
                {my_statistics_str}
            </a>""".format(course_id=course.get_id(), statistics_str=statistics_str,
                           my_statistics_str=my_statistics_str)
