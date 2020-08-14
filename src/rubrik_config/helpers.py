import importlib
import os
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


# Copied from https://github.com/pallets/werkzeug/blob/master/src/werkzeug/utils.py#L416
def secure_filename(filename: str) -> str:
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.  The filename returned is an ASCII only string
    for maximum portability.
    On windows systems the function also makes sure that the file is not
    named after one of the special device files.
    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename('i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'
    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you abort or
    generate a random filename if the function returned an empty one.
    .. versionadded:: 0.5
    :param filename: the filename to secure
    """
    if isinstance(filename, str):
        from unicodedata import normalize

        filename = normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(re.compile(r"[^A-Za-z0-9_.-]").sub("", "_".join(filename.split()))).strip("._")

    # On NT a couple of special files are present in each folder.  We have to ensure that the target 
    # file is not such a filename. In this case we prepend an underline.
    if (
        os.name == "nt"
        and filename
        and filename.split(".")[0].upper() in ("CON", "AUX", "COM1", "COM2", "COM3", "COM4", "LPT1", "LPT2", "LPT3", "PRN", "NUL")
    ):
        filename = f"_{filename}"

    return filename
