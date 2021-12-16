import web

import hashlib
import random
import json
from inginious.frontend.pages.utils import INGIniousPage 
from inginious.frontend.plugins.utils import get_mandatory_parameter

_LTI_REGISTRATION_TEMPLATES_PATH = "frontend/plugins/lti_register/pages/templates"

def get_user_lti(user_data):

    user_realname = user_data["realname"]
    user_email = user_data["email"]

    user_username = user_email.split('@')[0]

    lti_consumer = user_data["consumer_key"]

    new_user = {
        "username": user_username,
        "realname": user_realname,
        "email": user_email,
        "language": "es",
        "ltibindings": {
        },
    }

    return json.dumps(new_user)

class RegisterLTIPage(INGIniousPage):
    def is_lti_page(self):
        return False
    
    def add_static_files(self):
        self.template_helper.add_javascript("/lti_register/static/js/register_user_lti.js")

    def GET(self):

        data = web.input()
        new_user = json.loads(data.get("new_user",{}))

        self.add_static_files()

        return self.template_helper.get_custom_renderer(_LTI_REGISTRATION_TEMPLATES_PATH).lti_register(new_user)
    
    def POST(self):

        data = get_mandatory_parameter(web.input(), "data")

        course_id = data["courseid"]
        course = self._get_course_and_check_rights(course_id)

        if course is None:
            return 200,{"status":"error","text":"The course does not exist."}
        
        if not data["realname"] or not data["username"] or not data["email"]:
            return 200, {"status":"error","text":_("User cannot be registered. Some user data is no provided.")}

        user_data = {
            "username": data["username"] ,
            "realname": data["realname"],
            "email": data["email"]
        }

        return self.register_user(course, user_data)

    def register_user(self, course, user_data):

        user = self.database.users.find_one({"$or":[{"username":user_data["username"]},
                                                    {"email":user_data["email"]}
                                                    ]})
        if user is not None:

            if not self.user_manager.course_is_user_registered(course, user["username"]):
                return 200, {"status":"error","text":_("User cannot be registered. The user is not registered in this course.")}

        else:
            self.database.uses.insert({
                "username": user_data["username"],
                "email": user_data["email"],
                "realname": user_data["realname"],
                "password": "passEje"
            })

            return 200, {"status":"success","text":_("User was successfully registered.")}
        
        user_data = web.input()