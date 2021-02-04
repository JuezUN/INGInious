# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import web
import requests
import json
from inginious.frontend.pages.utils import INGIniousPage

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


def create_text_block(title, content):
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


def create_payload(data):
    blocks = [create_text_block("Asunto", subject_text[data["subject_id"]]),
              create_text_block("Email", data["email"]),
              create_text_block("Nombre", data["name"])]
    if is_new_course_request(data["subject_id"]):
        blocks.append(create_text_block("Nombre del curso", data["courseName"]))
    blocks.append(create_text_block("Comentario", data["textarea"]))
    return json.dumps({"blocks": blocks})


def send_request_to_slack(subject_id, payload):
    response = requests.post(URL_channel[subject_id], data=payload)
    print("Slack response: ", response)


def is_new_course_request(subject_id):
    return subject_id == subject_new_course_id


class ContactPage(INGIniousPage):
    def GET(self):
        return self.template_helper.get_custom_renderer(base_renderer_path).contact_page()

    def POST(self):
        data = web.input()
        payload = create_payload(data)
        send_request_to_slack(data["subject_id"], payload)
        return self.template_helper.get_custom_renderer(base_renderer_path).contact_page()
