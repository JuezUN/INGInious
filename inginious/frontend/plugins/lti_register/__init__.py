from .pages.lti_user_manager import get_lti_user

auth_id = None

def init(plugin_manager, course_factory, client, config):
    global auth_id 
    auth_id = config.get("id", None)

    plugin_manager.add_hook('lti_user', get_lti_user)