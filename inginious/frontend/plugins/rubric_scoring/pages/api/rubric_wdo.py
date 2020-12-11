# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Process json file for rubric scoring """
import json


class RubricWdo:
    """" Read the data of a json file """
    def __init__(self, source):
        self.data = self.read_data(source)

    def read_data(self, source):
        with open(source) as f:
            data = json.load(f)
            return data
