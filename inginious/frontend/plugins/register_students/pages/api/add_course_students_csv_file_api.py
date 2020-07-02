import web
import re
import hashlib
import random
import csv

from os.path import dirname, join
from inginious.frontend.plugins.utils.admin_api import AdminApi
from inginious.frontend.plugins.utils import get_mandatory_parameter, read_file

_static_folder_path = join(dirname(dirname(dirname(__file__))), "static")


class AddCourseStudentsCsvFile(AdminApi):
    def API_POST(self):
        """
        Method receiving POST request, receiving the file and course to register students on UNCode and the course.
        """
        file = get_mandatory_parameter(web.input(), "file")
        course_id = get_mandatory_parameter(web.input(), "course")

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
                         "text": _("The file is not formatted as expected, check it is comma separated ") + _(
                             "and emails are actual emails.")}

        registered_on_course, registered_users = self.register_all_students(parsed_file, course)

        message = _(
            """The process finished successfully. Registered students on the course: {0!s}. 
            Registered students on UNCode: {1!s}.""").format(
            registered_on_course, registered_users)

        return 200, {"status": "success", "text": message}

    def register_all_students(self, parsed_file, course):
        registered_on_course = 0
        registered_users = 0
        for user_data in parsed_file:
            data = self._parse_user_data(user_data)

            result = self._register_student(data)
            if result:
                registered_users += 1
            try:
                result = self.user_manager.course_register_user(course, data["username"], '', True)
                if result:
                    registered_on_course += 1
            except:
                pass

        return registered_on_course, registered_users

    def _register_student(self, data):
        """
        Registers the student in UNCode and sends a verification email to the user. If the user already exists, nothing
        happens.
        :param data: Dict containing the user data
        :return: True if succeeded the register. If user already exists returns False.
        """
        success = True

        existing_user = self.database.users.find_one(
            {"$or": [{"username": data["username"]}, {"email": data["email"]}]})
        if existing_user is not None:
            success = False
        else:
            passwd_hash = hashlib.sha512(data["passwd"].encode("utf-8")).hexdigest()
            activate_hash = hashlib.sha512(str(random.getrandbits(256)).encode("utf-8")).hexdigest()
            self.database.users.insert({"username": data["username"],
                                        "realname": data["realname"],
                                        "email": data["email"],
                                        "password": passwd_hash,
                                        "activate": activate_hash,
                                        "bindings": {},
                                        "language": self.user_manager._session.get("language", "en")})
            try:
                activate_account_link = web.ctx.home + "/register?activate=" + activate_hash
                email_template = read_file(_static_folder_path, "email_template.txt")
                web.sendmail(web.config.smtp_sendername, data["email"], _("Welcome on UNCode"),
                             email_template.format(activate_account_link))
            except:
                pass

        return success

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
        email = user_data[2]
        username = email.split("@")[0]

        data = {
            "realname": name + " " + lastname,
            "username": username,
            "email": email,
            "passwd": username
        }

        return data

    def _file_well_formatted(self, parsed_file):
        """
        Checks that the email has the required information, with three columns, emails at last column and with the right
        format.
        :return: True if the file correctly formatted. Otherwise returns False.
        """
        for data in parsed_file:
            if len(data) != 3:
                return False
            elif self._check_email_format(data[2]) is None:
                return False

        return True

    def _parse_csv_file(self, csv_file):
        """
        Method that parses the csv file, splitting each row by commas and strips every cell.
        :param csv_file: receives a string containing all information (e.g. "  name,  lastname,  email \n")
        :return: Matrix with the file parsed. The returned value looks like: [["name","lastnanme","email"]]
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
