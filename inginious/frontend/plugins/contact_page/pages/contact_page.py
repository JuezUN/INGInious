# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Contact page """

import json
import web
import requests
from inginious.frontend.pages.utils import INGIniousPage
from .constants import get_url_channel, get_subject_new_course_id, get_use_minify

base_renderer_path = "frontend/plugins/contact_page/pages/templates"


def generate_slack_request_payload(data):
    """ Create the payload to be sent """
    subject_text = {
        "subject-comment": "Report a problem or make a comment",
        "subject-new-course": "Request to create a new course",
    }
    blocks = [create_slack_text_block("Subject", subject_text[data["subject_id"]]),
              create_slack_text_block("Email", data["email"]),
              create_slack_text_block("Name", data["name"])]
    if is_new_course_request(data["subject_id"]):
        blocks.append(create_slack_text_block("Course Name", data["courseName"]))
    blocks.append(create_slack_text_block("Comments", data["textarea"]))
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
    """ Send a post request to some Slack channel (previously defined ) whit the user message """
    slack_url = get_url_channel()
    requests.post(slack_url[subject_id], data=payload)


def is_new_course_request(subject_id):
    """ Return true value if the subject of the message is create a new course """
    return subject_id == get_subject_new_course_id()


class ContactPage(INGIniousPage):
    """ Contact page """

    def GET(self):
        """ Get request. Return the contact page """
        self.add_js_and_css_files()
        return self.template_helper.get_custom_renderer(base_renderer_path).contact_page()

    def POST(self):
        """ Post request. send a message to slack """
        data = web.input()
        subject_id = data["subject_id"]
        payload = generate_slack_request_payload(data)
        send_request_to_slack(subject_id, payload)
        self.add_js_and_css_files()
        return self.template_helper.get_custom_renderer(base_renderer_path).contact_page()

    def add_js_and_css_files(self):
        """ Add the the js and css files depending if use minify """
        if get_use_minify():
            self.template_helper.add_javascript("/contact_page/static/js/contact_page.min.js")
            self.template_helper.add_css("/contact_page/static/css/contact_page.min.css")
        else:
            self.template_helper.add_javascript("/contact_page/static/js/contact_page_main.js")
            self.template_helper.add_javascript("/contact_page/static/js/contact_page_form.js")
            self.template_helper.add_javascript("/contact_page/static/js/message_box.js")
            self.template_helper.add_css("/contact_page/static/css/contact_page.css")
