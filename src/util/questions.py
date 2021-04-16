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
# Copyright (C) 2021 Mattia Milani <mattia.milani@studenti.unitn.it>

"""
Questions module
================

This module is used to keep the questions for the PyInquirer package.

"""

from PyInquirer import Separator
from PyInquirer import Validator, ValidationError
import strings as s
import os.path
import re


class int_validator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message=s.not_a_number_error,
                cursor_position=len(document.text))


class integer_list_validator(Validator):
    def validate(self, document):
        try:
            l = list(document.text.split())
            l2 = list(map(int, l))
        except ValueError:
            raise ValidationError(
                message=s.not_a_number_list_error,
                cursor_position=len(document.text))


class positive_int_validator(Validator):
    def validate(self, document):
        try:
            value = int(document.text)
            if value < 0:
                raise ValidationError(
                    message=s.number_lower_error,
                    cursor_position=len(document.text))
        except ValueError:
            raise ValidationError(
                message=s.not_a_number_error,
                cursor_position=len(document.text))


class nodes_validator(Validator):
    def validate(self, document):
        try:
            value = int(document.text)
            if value <= 1:
                raise ValidationError(
                    message=s.number_lower_error,
                    cursor_position=len(document.text))
        except ValueError:
            raise ValidationError(
                message=s.not_a_number_error,
                cursor_position=len(document.text))


class destination_validator(Validator):
    def validate(self, document):
        try:
            value = int(document.text)
            if value < 1:
                raise ValidationError(
                    message=s.number_lower_error,
                    cursor_position=len(document.text))
        except ValueError:
            raise ValidationError(
                message=s.not_a_number_error,
                cursor_position=len(document.text))


class json_validator(Validator):
    def validate(self, document):
        if not os.path.isfile(document.text) or\
                not document.text.split('.')[-1] == "json":
            raise ValidationError(
                message=s.invalid_json_file,
                cursor_position=len(document.text))


class graphml_validator(Validator):
    def validate(self, document):
        if not os.path.isfile(document.text) or\
                not document.text.split('.')[-1] == "graphml":
            raise ValidationError(
                message=s.invalid_graphml_file,
                cursor_position=len(document.text))


class folder_validator(Validator):
    def validate(self, document):
        if not os.path.isdir(document.text):
            raise ValidationError(
                message=s.invalid_folder,
                cursor_position=len(document.text))

class signal_validator(Validator):
    def validate(self, document):
        pattern = re.compile('^[AW]+$')
        if not re.search(pattern, document.text):
            raise ValidationError(
                    message=s.invalid_signal_sequence,
                    cursor_position=len(document.text))


generic_file_load = [
    {
        'type': 'input',
        'name': s.generic_file_load_name,
        'message': s.generic_file_load_message,
    }
]

generic_folder_load = [
    {
        'type': 'input',
        'name': s.generic_folder_name,
        'message': s.generic_folder_message,
        'validate': folder_validator,
        'filter': lambda folder_path: folder_path[:-1] \
                if folder_path[-1] == "/" else folder_path
    }
]


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

graph_definition = [
    {
        'type': 'input',
        'name': s.graph_name_name,
        'message': s.graph_name_message,
        'filter': lambda graph_name: graph_name + ".graphml" \
                if ".graphml" not in graph_name else graph_name
    },
    generic_folder_load[0],
    {
        'type': 'list',
        'name': s.graph_type_list_name,
        'message': s.graph_type_list_message,
        'choices': s.graph_type_list,
    },
    {
        'type': 'input',
        'name': s.graph_nodes_number_name,
        'message': s.graph_nodes_number_message,
        'validate': nodes_validator,
    },
    {
        'type': 'confirm',
        'name': s.graph_policies_name,
        'message': s.graph_policies_message,
        'default': True,
    },
    {
        'type': 'input',
        'name': s.graph_seed_name,
        'message': s.graph_seed_message,
        'default': "1234",
        'validate': int_validator,
    }
]

use_graph_centrality = [
    {
        'type': 'confirm',
        'name': s.use_graph_centrality_name,
        'message': s.use_graph_centrality_message,
        'default': True,
    }
]

graph_centrality = [
    {
        'type': 'list',
        'name': s.graph_centrality_name,
        'message': s.graph_centrality_message,
        'choices': s.graph_centrality_list,
    }
]

graph_destination_intro = [
    {
        'type': 'input',
        'name': s.graph_destination_number_name,
        'message': s.graph_destination_number_message,
        'validate': destination_validator,
    },
    {
        'type': 'list',
        'name': s.graph_dst_strategy_name,
        'message': s.graph_dst_strategy_message,
        'choices': s.graph_dst_strategy_list,
    },
    {
        'type': 'input',
        'name': s.graph_dst_seed_name,
        'message': s.graph_dst_seed_message,
        'default': "1234",
        'validate': int_validator,
    }
]

use_hier_dst = [
    {
        'type': 'input',
        'name': s.graph_dst_hier_name,
        'message': s.graph_dst_hier_message,
        'default': "1",
        'validate': int_validator,
    }
]

use_MRAI = [
    {
        'type': 'confirm',
        'name': s.use_graph_MRAI_name,
        'message': s.use_graph_MRAI_message,
        'default': True,
    }
]

graph_MRAI_intro = [
    {
        'type': 'list',
        'name': s.graph_MRAI_strategy_name,
        'message': s.graph_MRAI_strategy_message,
        'choices': s.graph_MRAI_strategies_list,
    },
    {
        'type': 'input',
        'name': s.graph_MRAI_value_name,
        'message': s.graph_MRAI_value_message,
        'default': "30",
        'validate': positive_int_validator,
    },
    {
        'type': 'input',
        'name': s.graph_MRAI_seed_name,
        'message': s.graph_MRAI_seed_message,
        'default': "1234",
        'validate': int_validator,
    },
    {
        'type': 'input',
        'name': s.graph_MRAI_mean_name,
        'message': s.graph_MRAI_mean_message,
        'default': "-1",
        'validate': int_validator,
    }
]

use_RFD = [
    {
        'type': 'confirm',
        'name': s.use_graph_RFD_name,
        'message': s.use_graph_RFD_message,
        'default': True,
    }
]

graph_RFD_intro = [
    {
        'type': 'list',
        'name': s.graph_RFD_strategy_name,
        'message': s.graph_RFD_strategy_message,
        'choices': s.graph_RFD_strategies_list,
    },
]

environment_load = [
    {
        'type': 'confirm',
        'name': s.load_env_name,
        'message': s.load_env_message,
        'default': True,
    }
]

environment_definition = [
    {
        'type': 'input',
        'name': s.env_file_name,
        'message': s.env_file_message,
        'filter': lambda env_name: env_name + ".json" \
                if ".json" not in env_name else env_name
    },
    generic_folder_load[0],
    {
        'type': 'input',
        'name': s.environment_tag_name,
        'message': s.env_name_message,
        'default': s.environment_default_name,
    },
    {
        'type': 'input',
        'name': s.environment_tag_seed,
        'message': s.env_seeds_message,
        'validate': integer_list_validator,
        'filter': lambda env_seed: str(list(map(int, list(env_seed.split()))))
    },
    {
        'type': 'input',
        'name': s.environment_tag_duration,
        'message': s.env_duration_message,
        'validate': positive_int_validator,
    },
    {
        'type': 'input',
        'name': s.environment_tag_output,
        'message': s.env_output_message,
        'default': s.environment_default_output,
    },
    {
        'type': 'confirm',
        'name': s.environment_tag_s_flag,
        'message': s.env_signal_flag_message,
        'default': True,
    },
    {
        'type': 'input',
        'name': s.environment_tag_s_sequence,
        'message': s.env_signal_message,
        'default': s.environment_default_s_sequence,
        'validate': signal_validator,
        'when': lambda answers: answers[s.environment_tag_s_flag]
    },
    {
        'type': 'confirm',
        'name': s.environment_tag_iw_flag,
        'message': s.env_iw_flag_message,
        'default': True,
    },
    {
        'type': 'confirm',
        'name': s.environment_tag_w_flag,
        'message': s.env_w_flag_message,
        'default': True,
        'when': lambda answers: not answers[s.environment_tag_s_flag]
        },
    {
        'type': 'confirm',
        'name': s.environment_tag_r_flag,
        'message': s.env_r_flag_message,
        'default': True,
        'when': lambda answers: not answers[s.environment_tag_s_flag]
    }
]

experiments = [
    {
        'type': 'list',
        'name': s.exp_type_name,
        'message': s.exp_type_message,
        'choices': s.exp_type_list,
    },
    {
        'type': 'input',
        'name': s.exp_single_run_sim_name,
        'message': s.exp_single_run_sim_message,
        'default': s.environment_default_name,
        'when': lambda answers: answers[s.exp_type_name] == s.exp_single_run
    },
    {
        'type': 'input',
        'name': s.exp_single_run_id_name,
        'message': s.exp_single_run_id_message,
        'default': '0',
        'validate': positive_int_validator,
        'when': lambda answers: answers[s.exp_type_name] == s.exp_single_run
    }
]

