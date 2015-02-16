# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
from os.path import isfile, join

from platformio import __version__
from platformio.exception import InvalidSettingName, InvalidSettingValue
from platformio.util import get_home_dir

DEFAULT_SETTINGS = {
    "check_platformio_interval": {
        "description": "Check for the new PlatformIO interval (days)",
        "value": 3
    },
    "check_platforms_interval": {
        "description": "Check for the platform updates interval (days)",
        "value": 7
    },
    "check_libraries_interval": {
        "description": "Check for the library updates interval (days)",
        "value": 7
    },
    "auto_update_platforms": {
        "description": "Automatically update platforms (Yes/No)",
        "value": True
    },
    "auto_update_libraries": {
        "description": "Automatically update libraries (Yes/No)",
        "value": True
    },
    "enable_telemetry": {
        "description": ("Shares commands, platforms and libraries usage"
                        " to help us make PlatformIO better (Yes/No)"),
        "value": True
    },
    "enable_prompts": {
        "description": (
            "Can PlatformIO communicate with you via prompts: "
            "propose to install platforms which aren't installed yet, "
            "paginate over library search results and etc.)? ATTENTION!!! "
            "If you call PlatformIO like subprocess, "
            "please disable prompts to avoid blocking (Yes/No)"),
        "value": True
    }
}


class State(object):

    def __init__(self, path=None):
        self.path = path
        if not self.path:
            self.path = join(get_home_dir(), "appstate.json")
        self._state = {}

    def __enter__(self):
        try:
            if isfile(self.path):
                with open(self.path, "r") as fp:
                    self._state = json.load(fp)
        except ValueError:
            self._state = {}
        return self._state

    def __exit__(self, type_, value, traceback):
        with open(self.path, "w") as fp:
            if "dev" in __version__:
                json.dump(self._state, fp, indent=4)
            else:
                json.dump(self._state, fp)


def get_state_item(name, default=None):
    with State() as data:
        return data.get(name, default)


def set_state_item(name, value):
    with State() as data:
        data[name] = value


def get_setting(name):
    if name not in DEFAULT_SETTINGS:
        raise InvalidSettingName(name)

    with State() as data:
        if "settings" in data and name in data['settings']:
            return data['settings'][name]

    return DEFAULT_SETTINGS[name]['value']


def set_setting(name, value):
    if name not in DEFAULT_SETTINGS:
        raise InvalidSettingName(name)

    defdata = DEFAULT_SETTINGS[name]
    try:
        if "validator" in defdata:
            value = defdata['validator']()
        elif (isinstance(defdata['value'], bool) and
              not isinstance(value, bool)):
            value = str(value).lower() in ("yes", "y", "1")
        elif isinstance(defdata['value'], int):
            value = int(value)
    except Exception:
        raise InvalidSettingValue(value, name)

    with State() as data:
        if "settings" not in data:
            data['settings'] = {}
        data['settings'][name] = value


def reset_settings():
    with State() as data:
        if "settings" in data:
            del data['settings']
