import web
import re
import hashlib
import random
import csv
import string
import threading

from os.path import dirname, join
from inginious.frontend.plugins.utils.admin_api import AdminApi
from inginious.frontend.plugins.utils import get_mandatory_parameter

_static_folder_path = join(dirname(dirname(dirname(__file__))), "static")


class AddCourseStudentsCsvFile(AdminApi):
    def API_POST(self):
        """
        Method receiving POST request, receiving the file and course to register students on UNCode and the course.
        """
        file = get_mandatory_parameter(web.input(), "file")
        course_id = get_mandatory_parameter(web.input(), "course")
        email_language = get_mandatory_parameter(web.input(), "language")

        if email_language not in self.app.available_languages:
            return 200, {"status": "error",
                         "text": _("Language is not available.")}

        course = self._get_course_and_check_rights(course_id)
        if course is None:
            return 200, {"status": "error",
                         "text": _("The course does not exist or the user does not have permissions.")}

        try:
            text = file.decode("utf-8")
        except:
            return 200, {"status": "error", "text": _("The file is not coded in UTF-8. Please change the encoding.")}

        parsed_file = self._parse_csv_file(text)

        if not self._file_well_formatted(parsed_file):
            return 200, {"status": "error",
                         "text": _(
                             """The file is not formatted as expected, check it is comma separated and 
                             emails are actual emails.""")}

        session_language = self.user_manager.session_language()
        self.user_manager.set_session_language(email_language)
        registered_on_course, registered_users, users_failed = self.register_all_students(parsed_file, course,
                                                                                          email_language)
        self.user_manager.set_session_language(session_language)

        total_to_register = len(parsed_file)
        message = _(
            """The process finished with {0!s} students registered on the course and {1!s} students registered 
            on UNCode out of {2!s} students listed in the file. The emails for the new students are being sent in the 
            background, wait a while and check again that all the students were registered.""").format(
            registered_on_course, registered_users, total_to_register)

        if len(users_failed) > 0:
            html_users_failed = "".join(
                map(lambda x: "<br>  - {} - {}".format(x["username"], x["email"]), users_failed))
            failed_students_message = _(
                """<br><br>The next students were not registered because of an unexpected error, probably the user 
                is already registered with another username or the username is already taken:
                {}""".format(html_users_failed))
            message += failed_students_message

        return 200, {"status": "success", "text": message}

    def register_all_students(self, parsed_file, course, email_language):
        registered_on_course = 0
        registered_users = 0
        all_emails = []
        users_failed = []
        for user_data in parsed_file:
            data = self._parse_user_data(user_data)

            was_registered, email, failed = self._register_student(data, course, email_language)
            if was_registered:
                registered_users += 1
                all_emails.append(email)

            if self._is_failed_register(was_registered, failed, data):
                users_failed.append(data)
                continue

            try:
                was_registered_on_course = self.user_manager.course_register_user(course, data["username"], '', True)
                if was_registered_on_course:
                    registered_on_course += 1
            except:
                pass

        # Send the emails in the background as this may take a long time.
        emails_thread = threading.Thread(target=self._send_emails_in_background,
                                         args=[all_emails, self.database.users.delete_one])
        emails_thread.start()
        return registered_on_course, registered_users, users_failed

    def _is_failed_register(self, was_registered, failed, data):
        """
        Check when the student was not registered on UNCode but still does not exist in DB, thus, the student is
        already registered on UNCode with a different username or the username was already taken with another email.
        Also check if the register failed due to an unexpected error.
        """

        user = self.database.users.find_one({"username": data["username"]})

        return (not was_registered and user is None) or (user is not None and user["email"] != data["email"]) or failed

    def _register_student(self, data, course, email_language):
        """
        Registers the student in UNCode and sends a verification email to the user. If the user already exists, nothing
        happens.
        :param data: Dict containing the user data
        :return: True if succeeded the register. If user already exists returns False.
        """
        existing_user = self.database.users.find_one(
            {"$or": [{"username": data["username"]}, {"email": data["email"]}]})
        if existing_user is not None:
            return False, None, False
        password = data["password"]
        passwd_hash = hashlib.sha512(data["password"].encode("utf-8")).hexdigest()
        activate_hash = hashlib.sha512(str(random.getrandbits(256)).encode("utf-8")).hexdigest()
        data = {"username": data["username"],
                "realname": data["realname"],
                "email": data["email"],
                "password": passwd_hash,
                "activate": activate_hash,
                "bindings": {},
                "language": email_language
                }
        try:
            activate_account_link = web.ctx.home + "/register?activate=" + activate_hash
            data_policy_link = web.ctx.home + "/data_policy"
            content = str(
                self.template_helper.get_custom_renderer(_static_folder_path, False).email_template()).format(
                activation_link=activate_account_link, username=data["username"],
                password=password, course_name=course.get_name("en"), data_policy=data_policy_link)
            self.database.users.insert(data)
        except:
            return False, None, True

        email = (data["email"], content)
        return True, email, False

    def _send_emails_in_background(self, emails, delete_user_function):
        subject = _("Welcome on UNCode")
        headers = {"Content-Type": 'text/html'}
        for (email_address, email_content) in emails:
            try:
                web.sendmail(web.config.smtp_sendername, email_address, subject, email_content, headers)
            except:
                # Unregister student in case it failed to send the email.
                delete_user_function({"email": email_address})

    def _check_email_format(self, email):
        """Checks email matches a real email."""
        email_re = re.compile(
            r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
            r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
            r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain

        return email_re.match(email)

    def _parse_user_data(self, user_data):
        """
        Parses the user data into a dict.
        :param user_data: array containing the user data, That array comes from the parsed file.
        :return: Dict containing all parsed information.
        """
        name = user_data[0]
        lastname = user_data[1]
        username = user_data[2]
        email = user_data[-1]

        _password_length = 15
        data = {
            "realname": name + " " + lastname,
            "username": username,
            "email": email,
            "password": random_password(_password_length).replace("{", "{{").replace("}", "}}")
        }

        return data

    def _file_well_formatted(self, parsed_file):
        """
        Checks that the email has the required information, with three columns, emails at last column and with the right
        format.
        :return: True if the file correctly formatted. Otherwise returns False.
        """
        for data in parsed_file:
            if len(data) != 4:
                return False
            elif self._check_email_format(data[-1]) is None:
                return False

        return True

    def _parse_csv_file(self, csv_file):
        """
        Method that parses the csv file, splitting each row by commas and strips every cell.
        :param csv_file: receives a string containing all information (e.g. "  name,  lastname, username, email \n")
        :return: Matrix with the file parsed. The returned value looks like: [["name","lastnanme","username", "email"]]
        """
        csv_file = csv.reader(csv_file.splitlines(), delimiter=',')
        return [[cell.strip() for cell in row if cell] for row in csv_file if row]

    def _get_course_and_check_rights(self, course_id):
        """Retrieves the course, checks it exists and has admin rights on the course."""
        try:
            course = self.course_factory.get_course(course_id)
        except:
            return None

        if not self.user_manager.has_admin_rights_on_course(course):
            return None

        return course


def random_password(length):
    pool = string.ascii_letters + string.digits
    return ''.join(random.choice(pool) for _ in range(length))
