# coding=utf-8
from configparser import ConfigParser
from typing import Dict

import yaml

from kebab.exceptions import KebabException


class YamlLoader:
    # noinspection PyMethodMayBeStatic
    def load(self, content: str) -> Dict[str, Dict[str, str]]:
        return yaml.safe_load(content)


class IniLoader:
    def __init__(self):
        self._parser = ConfigParser()

    def load(self, content: str) -> Dict[str, Dict[str, str]]:
        self._parser.read_string(content)
        return {
            section: dict(self._parser.items(section))
            for section in self._parser.sections()
        }
