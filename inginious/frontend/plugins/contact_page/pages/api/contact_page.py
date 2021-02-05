# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

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

destination_email = ""


def set_destination_email(email):
    global destination_email
    destination_email = email


def set_url_channel(main_message_channel, new_course_channel):
    global URL_channel
    if main_message_channel != "":
        URL_channel["subject-comment"] = main_message_channel
        if new_course_channel != "":
            URL_channel["subject-new-course"] = new_course_channel
        else:
            URL_channel["subject-new-course"] = main_message_channel
    else:
        raise SlackURLError("The main slack's URL is empty")


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
    requests.post(URL_channel[subject_id], data=payload)


def is_new_course_request(subject_id):
    return subject_id == subject_new_course_id


def send_email(data):
    subject = define_email_subject(subject_text[data["subject_id"]], data["courseName"])
    content = define_email_content(data)
    #
    from_email = web.config.smtp_sendername
    web.sendmail(from_email, destination_email, subject, content)


def define_email_subject(data_subject, course_name):
    subject = data_subject
    if course_name != "":
        subject += "-" + course_name
    return subject


def define_email_content(data):
    content = "Nombre: " + data["name"] + "\n"
    content += "Email: " + data["email"] + "\n"
    content += "Comentario:\n" + data["textarea"]
    return content


class ContactPage(INGIniousPage):
    def GET(self):
        return self.template_helper.get_custom_renderer(base_renderer_path).contact_page()

    def POST(self):
        data = web.input()
        subject_id = data["subject_id"]
        payload = create_payload(data)
        send_request_to_slack(subject_id, payload)
        """ 
        if subject_id == subject_new_course_id and destination_email != "":
            send_email(data)"""
        return self.template_helper.get_custom_renderer(base_renderer_path).contact_page()
