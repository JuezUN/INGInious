from email import header
import web

import hashlib
import random
import json
from inginious.common.course_factory import InvalidNameException, CourseNotFoundException
from inginious.frontend.pages.api._api_page import APIError
from inginious.frontend.pages.utils import INGIniousPage 
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.register_students.pages.api.add_course_students_csv_file_api import random_password
from .constants import use_minified

_LTI_REGISTRATION_TEMPLATES_PATH = "frontend/plugins/lti_register/pages/templates"
_EMAIL_REGISTER_USER_TEMPLATES_PATH = "frontend/plugins/register_students/static"

def get_user_lti(user_data):

    user_realname = user_data["realname"]
    user_email = user_data["email"]

    user_username = user_data["username"]

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

    """
    Page called by the LTI Login page to register a new user
    """
    def is_lti_page(self):
        return False
    
    def add_static_files(self, template_helper):
        if use_minified():
            template_helper.add_javascript("/lti_register/static/js/register_user_lti.min.js")
        else:
            template_helper.add_javascript("/lti_register/static/js/register_user_lti.js")

    def GET(self):

        data = web.input()
        
        new_user = data.get("new_user",{})
        parsed_new_user = {}

        if new_user:

            parsed_new_user = json.loads(new_user)

        self.add_static_files(self.template_helper)

        return self.template_helper.get_custom_renderer(_LTI_REGISTRATION_TEMPLATES_PATH).lti_register(parsed_new_user, self.user_manager.session_logged_in())
    
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

        all_messages = []

        try:
            success_user_registration, to_send_email = self.register_user(course, user_data)
        except:
            raise APIError(400, {"error": _("An error occurred while registering the user.")})

        if success_user_registration:

            try:
                subject = _("Welcome on UNCode")

                self.send_email(subject, user_data, to_send_email)
                all_messages.append({"status":"success","message":_("Your UNCode account was successfully created!. An email was sent to you with your account credentials.")})
            except:
                self.database.users.delete_one({"username":user_data["username"], "email": user_data["email"]})
                all_messages.append({"status": "error", "message": _("The new user was not created. There was an error sending the email.")})
    
        else:
            all_messages.append({"status": "error", "message": _("The new user was not created. Maybe the username or email were already taken.")})
            
        is_user_registered_in_course = None

        try:
            is_user_registered_in_course = self.register_in_course(course, user_data["username"])
        except:
            raise APIError(400, {"error": _("An error occurred while registering the user in the course.")})

        if is_user_registered_in_course:
            all_messages.append({"status":"success","message":_("Your user was registered in the course. Please check the email that was sent to you with the information of the course you have been enrolled to.")})
            if not success_user_registration and to_send_email:
                try:
                    subject = _("You have been enrolled on a course")
                    self.send_email(subject, user_data, to_send_email)
                except:
                    all_messages.append({"status":"error","message":_("There was an error sending the course registration email.")})
        else:
            all_messages.append({"status":"error","message":_("You were not registered in the course. Your are already registered in the course, you have no permissions or there is no a created user with the provided data")})

        return {"all_messages": all_messages}
        

    def register_user(self, course, user_data):

        """
        Register a new user to UNCode
        
        :param course: Course in which the user will be registered
        :param user_data: The user data requiered to create a new account 
        :return: Retrun a tuple with a True value when a new user is created, and a email template.
        """
        user_exists = self.already_user_exists(user_data["username"], user_data["email"])

        if user_exists:
            return False, self.course_registration_email(user_data["username"], course)

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
            to_send_email = self.registration_email(user_data["username"], course, password, user_activation_hash)

            self.database.users.insert(user_data)
        except:
            return False, None
        
        return True, to_send_email
        
    def register_in_course(self, course, username):
        """
        Register a user in a course
        
        :return: Return True if the user was registered in thecourse.
        """

        user_registered_in_course = None

        user_registered_in_course = self.user_manager.course_register_user(course, username, '', True)

        return user_registered_in_course

    def send_email(self, subject, user_data, to_send_email):
        """
        Send a registration email to a user

        :param subject: An email subject
        :param user_data: Receiving user data 
        :param to_send_email: The email template
        """

        headers = {"Content-Type": 'text/html'}

        web.sendmail(web.config.smtp_sendername, user_data["email"], subject, to_send_email, headers)

    def registration_email(self, username, course, user_password, user_activation_hash):
        """
        Format the new user registration email template to be sent
        """
        user_activation_link = web.ctx.home + "/register?activate=" + user_activation_hash
        data_policy_link = web.ctx.home + "/data_policy"

        to_send_email = str(self.template_helper.get_custom_renderer(_EMAIL_REGISTER_USER_TEMPLATES_PATH, False).email_template()).format(
                activation_link=user_activation_link, username=username, password=user_password, course_name=course.get_name("en"), data_policy=data_policy_link
        )
        
        return to_send_email


    def course_registration_email(self, username, course):
        """
        Format the registration course email template to be sent
        """

        data_policy_link = web.ctx.home + "/data_policy"
        course_link = web.ctx.home + "/course/" + course.get_id()

        course_name = course.get_name("en")

        to_send_email = str(self.template_helper.get_custom_renderer(_EMAIL_REGISTER_USER_TEMPLATES_PATH, False).email_course_registration_template()).format(
            course_name=course_name, course_link=course_link, username=username, data_policy=data_policy_link
        )

        return to_send_email



    def already_user_exists(self, username, email):
        """
        Return True if user already exists
        """
        
        user = self.database.users.find_one({"$or": [{"username":username},{"email":email}]})

        if user:
            return True

        return False
