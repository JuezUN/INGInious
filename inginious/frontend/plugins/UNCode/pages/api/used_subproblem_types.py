import inginious.frontend.pages.api._api_page as api
from inginious.frontend.plugins.UNCode.constants import get_used_subproblem_types


class UsedSubproblemTypes(api.APIPage):
    def API_GET(self):
        return 200, get_used_subproblem_types()
