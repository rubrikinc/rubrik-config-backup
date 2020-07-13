import importlib
import re

import cli_ui
import rubrik_cdm


def config_class(module_name):
    class_name = module_name.title().replace('_', '') + 'Config'
    klass = getattr(importlib.import_module('rubrik_config.'+module_name), class_name)
    return klass


def config_name(obj):
    matches = re.findall('[A-Z][^A-Z]*', type(obj).__name__)
    name = '_'.join(matches[:-1])
    return name.lower()


def filter_fields(original, keepers):
    return { k: v for k, v in original.items() if k in keepers }


def cluster_name(rubrik):
    return rubrik.get('v1', '/cluster/me')['name']


def ask_multiline_string(ask):
    cli_ui.info(cli_ui.green, '::', cli_ui.lightgray, ask, '(blank line will terminate)')
    
    user_input = []
    is_first_line = True
    while True:
        if is_first_line:
            line = cli_ui.read_input()
            is_first_line = False
        else: 
            line = input()

        if not line: # If line is blank
            break
        else:
            user_input.append(line)

    return '\n'.join(user_input)


def ask_or_default(name, label, defaults={}):
    result = ''

    if name not in defaults.keys():
        result = cli_ui.ask_string(label+'?')
    else:
        result = defaults[name]
        cli_ui.info_1(label+':', result)
    
    return result


def status_color(status):
    color = cli_ui.yellow
    if status == 'SUCCEEDED': color = cli_ui.green
    elif status == 'FAILED': color = cli_ui.red
    return color
