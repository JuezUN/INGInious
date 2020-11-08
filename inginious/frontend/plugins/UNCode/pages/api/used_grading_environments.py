""" Get function for obtain _used_grading_environments array """
from inginious.frontend.plugins.UNCode.constants import get_used_grading_environments
import inginious.frontend.pages.api._api_page as api


class UsedGradingEnvironments(api.APIPage):
    def API_GET(self):
        return 200, get_used_grading_environments()
