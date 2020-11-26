import os

RENDERER_PATH = 'frontend/plugins/rubric_scoring/pages/templates'

BASE_STATIC_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../static')


def rubric_course_admin_menu_hook(course):
    return "rubric_scoring", '<i class="fa fa-bar-chart" aria-hidden="true"></i> Rubric Scoring'
