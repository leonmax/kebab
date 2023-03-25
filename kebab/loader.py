# coding=utf-8
import abc
from configparser import ConfigParser

import yaml


Context = dict[str, 'Context'] | list['Context'] | str | int | float | bool | None


# noinspection PyUnusedLocal
class StrLoader(object):
    @abc.abstractmethod
    def load(self, content: str) -> Context:
        return {}


class YamlLoader(StrLoader):
    # noinspection PyMethodMayBeStatic
    def load(self, content: str) -> Context:
        return yaml.safe_load(content)


class IniLoader(StrLoader):
    def __init__(self):
        self._parser = ConfigParser()

    def load(self, content: str) -> Context:
        self._parser.read_string(content)
        return {
            section: dict(self._parser.items(section))
            for section in self._parser.sections()
        }
