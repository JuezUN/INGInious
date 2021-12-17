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

        status_messages = []

        try:
            success_user_registration, to_send_email = self.register_user(course, user_data)
        except:
            raise APIError(400, {"error": _("An error has occurred while registering the user.")})

        if not success_user_registration:
            status_messages.append(json.dumps({"status": "error", "message": _("The new user was not created. Maybe this username or email are already taken.")}))
            
        is_user_registered_in_course = None
        try:
            is_user_registered_in_course  = self.register_in_course(course, user_data["username"])
        except:
            raise APIError(400, {"error": _("An error has occurred while registering the user in the coourse.")})

        if is_user_registered_in_course:
            status_messages.append(json.dumps({"status":"success","text":_("Your user was registered on curse.")}))
        else:
            status_messages.append(json.dumps({"status":"errpr","text":_("You were not registered on curse. Your are already registered in course or you have no permissions")}))


        if success_user_registration:
            try:
                self.send_email(user_data, to_send_email)
                status_messages.append(json.dumps({"status":"success","text":_("Your UNCode account was successfully created!. An email was sent to you with your account credentials.")}))
            except:
                self.database.users.delete_one({"username":user_data["username"], "email": user_data["email"]})
                status_messages.append(json.dumps({"status": "error", "message": _("The new user was not created. There was an error while sending the email.")}))

        return 200, status_messages
        

    def register_user(self, course, user_data):

        user_exists = self.already_user_exists(user_data["username"], user_data["email"])

        if user_exists:
            return False, None

        password = user_data["password"]

        user_password_hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
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
            to_send_email = str(self.template_helper.get_custom_renderer(_EMAIL_REGISTER_USER_TEMPLATES_PATH, False).email_template()).format(
                activation_link=user_activation_link, username=user_data["username"],
                password=password, course_name=course.get_name("en"), data_policy=data_policy_link)

            self.database.users.insert(user_data)
        except:
            return False, None
        
        return True, to_send_email
        
    def register_in_course(self, course, username):

        user_registered_in_course = None

        user_registered_in_course = self.user_manager.course_register_user(course, username, '', True)

        if user_registered_in_course:
            return True
        return False

    def send_email(self, user_data, to_send_email):

        subject = _("Welcome on UNCode")
        headers = {"Content-Type": 'text/html'}

        web.sendmail(web.config.smtp_sendername, user_data["email"], subject, to_send_email, headers)

    def already_user_exists(self, username, email):
        
        user = self.database.users.find_one({"$or": [{"username":username},{"email":email}]})

        if user:
            return True

        return False
