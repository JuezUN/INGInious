import json
import posixpath
import urllib
import web
import re

import inginious.frontend.pages.api._api_page as api
from inginious.frontend.pages.utils import INGIniousPage
from inginious.common.filesystems.local import LocalFSProvider


def read_file(file_path, file_name):
    with open(file_path + "/" + file_name, "r") as file:
        content_file = file.read()
    return content_file


def get_mandatory_parameter(parameters, parameter_name):
    if parameter_name not in parameters:
        raise api.APIError(400, {"error": parameter_name + _(" is mandatory")})

    return parameters[parameter_name]


def create_static_resource_page(base_static_folder):
    class StaticResourcePage(INGIniousPage):
        def GET(self, path):
            path_norm = posixpath.normpath(urllib.parse.unquote(path))

            static_folder = LocalFSProvider(base_static_folder)
            (method, mimetype_or_none, file_or_url) = static_folder.distribute(path_norm, False)

            if method == "local":
                web.header('Content-Type', mimetype_or_none)
                return file_or_url
            elif method == "url":
                raise web.redirect(file_or_url)

            raise web.notfound()

    return StaticResourcePage


def read_json_file(source):
    """ This function read a json file and return data """
    with open(source) as file:
        data = json.load(file)
        return data


def check_email_format(email):
    """ Checks email matches a real email."""
    email_re = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain
    return email_re.match(email)
