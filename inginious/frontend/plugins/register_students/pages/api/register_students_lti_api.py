import web

from inginious.frontend.plugins.utils.admin_api import AdminApi
from inginious.frontend.plugins.utils import get_mandatory_parameter

class RegisterStudentsLTIAPI(AdminAPI):

    def API_POST(self):

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
            


