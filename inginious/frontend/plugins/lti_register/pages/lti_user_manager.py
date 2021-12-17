import web

import hashlib
import random
import json
from inginious.common.course_factory import InvalidNameException, CourseNotFoundException
from inginious.frontend.pages.api._api_page import APIError
from inginious.frontend.pages.utils import INGIniousPage 
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.register_students.pages.api.add_course_students_csv_file_api import random_password

_LTI_REGISTRATION_TEMPLATES_PATH = "frontend/plugins/lti_register/pages/templates"
_EMAIL_REGISTER_USER_TEMPLATES_PATH = "frontend/plugins/register_students/static"

def get_user_lti(user_data):

    user_realname = user_data["realname"]
    user_email = user_data["email"]

    user_username = user_email.split('@')[0]

    task = user_data["task"]

    new_user = {
        "username": user_username,
        "realname": user_realname,
        "email": user_email,
        "language": "es",
        "ltibindings": {
        },
        "task": task
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

        new_user = get_mandatory_parameter(web.input(), "new_user")
        data = json.loads(new_user)

        (course_id, task_id)= data["task"]

        try:
            course = self.course_factory.get_course(course_id); 
        except (InvalidNameException, CourseNotFoundException):
            raise APIError(400, {"error": _("The course does not exist.")})
        
        if not data["realname"] or not data["username"] or not data["email"] or not course:
            return 200, {"status":"error","text":_("User cannot be registered. Some user data is no provided.")}

        user_data = {
            "username": data["username"] ,
            "realname": data["realname"],
            "email": data["email"],
            "language": data["language"],
            "ltibindings": data["ltibindings"],
            "password": random_password(15).replace("{", "{{").replace("}", "}}")
        }

        try:
            success_user_registration_message = self.register_user(course, user_data)
        except:
            raise APIError(400, {"error": _("An error has occurred while registering the user.")})

        return 200, success_user_registration_message
        

    def register_user(self, course, user_data):

        user_exists = self.already_user_exists(user_data["username"], user_data["email"])

        if user_exists:
            return False

        user_password_hash = hashlib.sha512(user_data["password"].encode("utf-8")).hexdigest()
        user_activation_hash = hashlib.sha512(str(random.getrandbits(256)).encode("utf-8")).hexdigest()

        user_data = {
            "username": user_data["username"] ,
            "realname": user_data["realname"],
            "email": user_data["email"],
            "language": user_data["language"],
            "ltibindings": user_data["ltibindings"],
            "password": user_password_hash,
            "activate": user_activation_hash,
            "bindings": {}
        }

        try:
            user_activation_link = web.ctx.home + "/register?activate=" + user_activation_hash
            data_policy_link = web.ctx.home + "/data_policy"
            email_template = str(self.template_helper.get_custom_renderer(_EMAIL_REGISTER_USER_TEMPLATES_PATH).email_template()).format(
                activation_link=user_activation_link, username=user_data["username"],
                password=user_data["password"], course_name=course.get_name("en"), data_policy=data_policy_link)

            self.database.users.insert(user_data)
        except:
            return json.dumps({"status": "error", "message": _("The new user was not created. Maybe this username or email are already taken")})
        
        is_user_registered_in_course  = self.register_in_course(course, user_data["username"])

        if is_user_registered_in_course:

            subject = _("Welcome on UNCode")
            headers = {"Content-Type": 'text/html'}

            try:
                web.sendmail(web.config.smtp_sendername, user_data["email"], subject, email_template, headers)
            except:
                return json.dumps({"status": "error", "message": _("There was an error while sending the email")})

        return json.dumps({"status":"succsess","text":_("Your UNCode account was successfully created!. You can now bind your new account.")})
        
    
    def register_in_course(self, course, username):

        user_registered_in_course = None

        try:
            user_registered_in_course = self.user_manager.course_register_user(course, username, '', True)
        except:
            pass

        if user_registered_in_course:
            return True
        return False


    def already_user_exists(self, username, email):
        
        user = self.database.users.find_one({"$or": [{"username":username},{"email":email}]})

        if user:
            return True

        return False
