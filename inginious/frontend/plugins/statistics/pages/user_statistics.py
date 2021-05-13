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
                .user_statistics(course, self._user_has_late_submissions(course_id))
        )

    def _user_has_late_submissions(self, course_id):
        """
        This checks whether the user has late submissions for the given course. In case the user does not have,
        the statistics tab for late submissions is not shown.
        """
        username = self.user_manager.session_username()
        data = list(
            self.database.submissions.find({"courseid": course_id, "username": username, "is_late_submission": True}))
        return len(data) > 0


def statistics_course_menu_hook(course, template_helper):
    student_tools_str = _("Student's Tools")
    my_statistics_str = _("My statistics")
    return """
            <h3>{student_tools_str}</h3>
            <a class="list-group-item list-group-item-info"
                href="/user_statistics/{course_id}">
                <i class="fa fa-line-chart"></i>
                {my_statistics_str}
            </a>""".format(course_id=course.get_id(), student_tools_str=student_tools_str,
                           my_statistics_str=my_statistics_str)
