from inginious.frontend.plugins.contact_page import SlackURLError

URL_channel = {
    "subject-comment": "",
    "subject-new-course": "",
}
SUBJECT_NEW_COURSE_ID = "subject-new-course"


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
