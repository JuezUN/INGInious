# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Contact page """

import web
import requests
import json
from inginious.frontend.pages.utils import INGIniousPage
from inginious.frontend.plugins.contact_page.pages.api.slack_url_error import SlackURLError

subject_text = {
    "subject-comment": "Comentario o reporte de un problema",
    "subject-new-course": "Peticion para crear un nuevo curso",
}
URL_channel = {
    "subject-comment": "",
    "subject-new-course": "",
}
subject_new_course_id = "subject-new-course"

base_renderer_path = "frontend/plugins/contact_page/pages/templates"


def set_url_channel(main_message_channel, new_course_channel):
    """ Define the URL directions where do the request """
    global URL_channel
    if main_message_channel != "":
        URL_channel["subject-comment"] = main_message_channel
        if new_course_channel != "":
            URL_channel["subject-new-course"] = new_course_channel
        else:
            URL_channel["subject-new-course"] = main_message_channel
    else:
        raise SlackURLError("The main slack's URL is empty")


def create_payload(data):
    """ Create the payload to be send """
    blocks = [create_slack_text_block("Asunto", subject_text[data["subject_id"]]),
              create_slack_text_block("Email", data["email"]),
              create_slack_text_block("Nombre", data["name"])]
    if is_new_course_request(data["subject_id"]):
        blocks.append(create_slack_text_block("Nombre del curso", data["courseName"]))
    blocks.append(create_slack_text_block("Comentario", data["textarea"]))
    return json.dumps({"blocks": blocks})


def create_slack_text_block(title, content):
    """ Create the blocks or sections of the message """
    text = "*%s:* \n %s" % (title, content)
    text = text.replace("\n", "\n>")
    text_content = {
        "type": "mrkdwn",
        "text": text
    }
    block_element = {
        "type": "section",
        "text": text_content
    }
    return block_element


def send_request_to_slack(subject_id, payload):
    """  """
    requests.post(URL_channel[subject_id], data=payload)


def is_new_course_request(subject_id):
    """  """
    return subject_id == subject_new_course_id


class ContactPage(INGIniousPage):
    """ Contact page """
    def GET(self):
        """ Get request. Return the contact page """
        return self.template_helper.get_custom_renderer(base_renderer_path).contact_page()

    def POST(self):
        """ Post request. send a message to slack """
        data = web.input()
        subject_id = data["subject_id"]
        payload = create_payload(data)
        send_request_to_slack(subject_id, payload)
        return self.template_helper.get_custom_renderer(base_renderer_path).contact_page()
