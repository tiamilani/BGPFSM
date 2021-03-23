#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the graphNU grapheneral Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# graphNU grapheneral Public License for more details.
#
# You should have received a copy of the graphNU grapheneral Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2020 Mattia Milani <mattia.milani@studenti.unitn.it>

"""
Questions module
================

This module is used to keep the questions for the PyInquirer package.

"""

from PyInquirer import Separator
from PyInquirer import Validator, ValidationError
import strings as s
import os.path

loading_questions = [
    {
        'type': 'confirm',
        'name': s.load_component_name,
        'message': s.load_conf,
        'default': True,
    }
]

graph_load = [
    {
        'type': 'confirm',
        'name': s.load_graph_name,
        'message': s.load_graph_message,
        'default': True,
    }
]

generic_file_load = [
    {
        'type': 'input',
        'name': s.generic_file_load_name,
        'message': s.generic_file_load_message,
    }
]


class graphml_validator(Validator):
    def validate(self, document):
        if not os.path.isfile(document.text) or\
                not document.text.split('.')[-1] == "graphml":
            raise ValidationError(
                message=s.invalid_graphml_file,
                cursor_position=len(document.text))

