from inginious.frontend.plugins.utils.admin_api import AdminApi
from ..constants import get_used_grading_environments


class UsedGradingEnvironments(AdminApi):
    def API_GET(self):
        return 200, get_used_grading_environments()