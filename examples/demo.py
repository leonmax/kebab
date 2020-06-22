#!/usr/bin/env python
import logging.config

import click

from examples.util import interval
from kebab import default_source, kebab_config, Field

k = default_source()
logging.config.dictConfig(k.subsource("logging"))


@kebab_config(auto_repr=True)
class DemoConfig:
    str_value = Field("ready", default_value="5", expected_type=str)
    int_value = Field("int", required=True, expected_type=int, masked=True)


@click.command()
@click.option('-w', '--watch', "by_secs", default=-1, type=float)
def cast(by_secs):
    while True:
        with interval(by_secs):
            value = k.cast("demo", DemoConfig)
            click.echo(value)


if __name__ == '__main__':
    # please reference to kebab cli for single get type of command
    cast()
