from inginious.frontend.plugins.utils.admin_api import AdminApi
from ..constants import get_used_subproblem_types


class UsedSubproblemTypes(AdminApi):
    def API_GET(self):
        return 200, get_used_subproblem_types()