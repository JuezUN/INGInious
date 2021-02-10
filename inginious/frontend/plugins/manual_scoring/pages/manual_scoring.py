# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Rubric scoring page """

import web

from bson.objectid import ObjectId

from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.plugins.manual_scoring.pages.rubric_wdo import RubricWdo
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.manual_scoring.pages import constants

base_renderer_path = constants.render_path


def define_content_of_comment_and_grade(submission):
    """  """
    comment = ""
    score = "No grade"

    if 'custom' in submission and 'comment' in submission['custom']:
        comment = submission['custom']['comment']

    if 'custom' in submission and 'rubric_score' in submission['custom']:
        score = submission['custom']['rubric_score']

    return comment, score


def get_submission_result_text(submission_input):
    info = submission_input['text']
    pars_text = ParsableText(info)
    final_text = pars_text.parse()
    final_text = final_text.replace('\n', '')
    return final_text


class ManualScoringPage(INGIniousAdminPage):
    """ Rubric scoring page to manual scoring """

    def GET_AUTH(self, course_id, task_id, submission_id):
        """ Get request """
        course, task = self.get_course_and_check_rights(course_id, task_id)

        self.template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-1.30.0.min.js")
        self.template_helper.add_javascript("https://cdn.jsdelivr.net/npm/lodash@4.17.4/lodash.min.js")

        return self.render_page(course, task, submission_id)

    def POST_AUTH(self, course_id, task_id, submission_id):
        """ POST request """
        course, task = self.get_course_and_check_rights(course_id, task_id)

        self.update_comment_and_grade(submission_id)

        return self.render_page(course, task, submission_id)

    def update_comment_and_grade(self, submission_id):
        """ update the grade and comment on db """
        data = web.input()

        if "grade" in data:
            self.database.submissions.update(
                {"_id": ObjectId(submission_id)},
                {"$set": {"custom.rubric_score": data["grade"]}
                 })
        elif "comment" in data:
            self.database.submissions.update(
                {"_id": ObjectId(submission_id)},
                {"$set": {"custom.comment": data["comment"]}
                 })

    def render_page(self, course, task, submission_id):
        """ Get all data and display the page """
        rubric_wdo = RubricWdo('inginious/frontend/plugins/manual_scoring/static/json/rubric.json')
        problem_id = task.get_problems()[0].get_id()
        submission = self.submission_manager.get_submission(submission_id, user_check=False)
        submission_input = self.submission_manager.get_input_from_submission(submission)
        comment, score = define_content_of_comment_and_grade(submission)

        data = {
            "url": 'manual_scoring',
            "summary": submission_input['custom']['custom_summary_result'],
            "grade": score,
            "language": submission_input['input'][problem_id + '/language'],
            "comment": comment,
            "score": submission_input['grade'],
            "task_name": course.get_task(submission_input['taskid']).get_name(self.user_manager.session_language()),
            "result": submission_input['result'],
            "feedback_result_text": get_submission_result_text(submission_input),
            "problem": submission_input['input'][problem_id],
            "username": submission_input['username'][0],
            "name": self.user_manager.get_user_realname(submission_input['username'][0]),
            "env": task.get_environment(),
            "question_id": problem_id,
            "submission_id": submission_id
        }

        return (
            self.template_helper.get_custom_renderer(base_renderer_path).rubric_scoring(
                course, task,
                rubric_wdo.read_data('inginious/frontend/plugins/manual_scoring/static/json/rubric.json'), data)
        )
