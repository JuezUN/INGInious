import hashlib
import random

def get_lti_user(user_data):

    user_realname = user_data["realname"]
    user_email = user_data["email"]

    user_username = user_email.split('@')[0]

    lti_consumer = user_data["consumer_key"]

    new_user = {
        "username": user_username,
        "realname": user_realname,
        "email": user_email,
        "language": "es",
        "ltibindings": {
            user_data["task"][0]:{
                lti_consumer: user_data["username"]
            }
        },
    }

    return new_user