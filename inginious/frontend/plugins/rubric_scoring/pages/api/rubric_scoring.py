import web
import os
from inginious.frontend.plugins.rubric_scoring.pages.api.rubric_wdo import RubricWdo
from bson.objectid import ObjectId

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage

from inginious.frontend.plugins.rubric_scoring.pages.api import pages

base_renderer_path = pages.RENDERER_PATH

base_static_folder = pages.BASE_STATIC_FOLDER


class RubricScoringPage(INGIniousAdminPage):

    def POST_AUTH(self, course_id, task_id, submission_id):
        """ POST request """
        course, task = self.get_course_and_check_rights(course_id, task_id)
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

        return self.page(course, task, submission_id)

    def GET_AUTH(self, course_id, task_id, submission_id):
        course, task = self.get_course_and_check_rights(course_id, task_id)

        self.template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-1.30.0.min.js")
        self.template_helper.add_javascript("https://cdn.jsdelivr.net/npm/lodash@4.17.4/lodash.min.js")

        return self.page(course, task, submission_id)

    def page(self, course, task, submission_id):

        # TODO: verificar que exista exactamente un elemento. TOMAR MEDIDAS PREVENTIVAS EN CASO CONTRARIO
        problem_id = task.get_problems()[0].get_id()

        submission = self.submission_manager.get_submission(submission_id, user_check=False)
        submission_input = self.submission_manager.get_input_from_submission(submission)
        name = self.user_manager.get_user_realname(submission_input['username'][0])


        comment = ""
        if ('custom' in submission and 'comment' in submission['custom']):
            comment = submission['custom']['comment']

        score = "No grade"
        if 'custom' in submission and 'rubric_score' in submission['custom']:
            score = submission['custom']['rubric_score']

        language = submission_input['input'][problem_id + '/language']

        task_name = course.get_task(submission_input['taskid']).get_name(self.user_manager.session_language())
        info = submission_input['text']
        aux_info = info.replace('\n\n.. raw:: html\n\n\t', '')
        aux_info_2 = aux_info.replace('\n', '')
        data = {
            "url": 'rubric_scoring',
            "summary": submission_input['custom']['custom_summary_result'],
            "grade": score,
            "language": language,
            "comment": comment,
            "score": submission_input['grade'],
            "task_name": task_name,
            "result": submission_input['result'],
            "text": aux_info_2,
            "problem_id": submission_input['input'][problem_id],
            "username": submission_input['username'][0],
            "name": name
        }

        rubric_wdo = RubricWdo('inginious/frontend/plugins/rubric_scoring/static/json/rubric.json')

        return (
            self.template_helper.get_custom_renderer(base_renderer_path).rubric_scoring(
                course, task,
                rubric_wdo.read_data('inginious/frontend/plugins/rubric_scoring/static/json/rubric.json'), data)
        )
