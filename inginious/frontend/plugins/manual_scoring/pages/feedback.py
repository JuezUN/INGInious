# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
""" Feedback view for the students """
from inginious.frontend.pages.api._api_page import APIError
from inginious.frontend.pages.utils import INGIniousAuthPage
from inginious.frontend.parsable_text import ParsableText
from ..constants import get_render_path, get_use_minify, get_dict_value
from .rubric import get_manual_scoring_data, get_rubric_content, add_static_files_to_render_notebook

base_renderer_path = get_render_path()


class FeedbackPage(INGIniousAuthPage):
    def GET_AUTH(self, course_id, submission_id):
        """ Get request """
        course = self.course_factory.get_course(course_id)
        submission = self.submission_manager.get_input_from_submission(self.get_submission(submission_id))
        add_static_files_to_render_notebook(self.template_helper)
        self.add_css_and_js_file()
        return self.render_page(course, submission)

    def render_page(self, course, submission):
        """ Get all data and display the page """
        rubric_content = get_rubric_content(self.user_manager, course.get_fs())
        comment, score, rubric_status = get_manual_scoring_data(submission)
        task_id = submission['taskid']
        task = self.get_task(course, task_id)
        problem_id = task.get_problems()[0].get_id()

        data = {
            "summary": get_dict_value(submission, "custom", "custom_summary_result"),
            "grade": score,
            "language": get_dict_value(submission, "input", problem_id + '/language'),
            "comment": ParsableText(comment,submission.get("response_type","rst")),
            "score": get_dict_value(submission, "grade"),
            "task_name": task.get_name_or_id(self.user_manager.session_language()),
            "result": submission['result'],
            "problem": submission['input'][problem_id],
            "environment_type": get_dict_value(submission, "input", problem_id + '/type'),
            "question_id": problem_id,
            "submission_id": submission['_id'],
            "rubric_status": rubric_status
        }

        return self.template_helper.get_custom_renderer(base_renderer_path).feedback(course, rubric_content, data, task)

    def get_submission(self, submission_id):
        """ get a submission by id """
        submission = self.submission_manager.get_submission(submission_id)
        if submission is None:
            raise APIError(404, "Submission no found")
        return submission

    def get_task(self, course, task_id):
        """ get a task """
        task = self.task_factory.get_task(course, task_id)
        return task

    def add_css_and_js_file(self):
        """ Add the css and js files """
        if get_use_minify():
            self.template_helper.add_javascript("/manual_scoring/static/js/feedback.min.js")
            self.template_helper.add_javascript("/manual_scoring/static/js/common_files.min.js")
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.min.css")
        else:
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.css")
            self.template_helper.add_javascript("/manual_scoring/static/js/code_area.js")
            self.template_helper.add_javascript("/static/js/message_box.js")
            self.template_helper.add_javascript("/manual_scoring/static/js/rubric.js")
            self.template_helper.add_javascript("/manual_scoring/static/js/manual_scoring_constants.js")
            self.template_helper.add_javascript("/manual_scoring/static/js/feedback_main.js")
