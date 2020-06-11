#!/usr/bin/env python
import json

import click

from examples.util import interval
from kebab import default_source, kebab_config, Field

source = default_source()


@kebab_config(auto_repr=True)
class DemoConfig:
    str_value = Field("ready", default_value=5)
    int_value = Field("int", required=True, expected_type=int)


@click.group()
def cli():
    pass


@cli.command()
@click.option('-i', '--interval', "by_secs", default=-1, type=float)
def cast(by_secs):
    while True:
        with interval(by_secs):
            value = source.cast("demo", DemoConfig)
            click.echo(value)


@cli.command()
@click.option('-i', '--interval', "by_secs", default=-1, type=float)
@click.argument('key', default='.', nargs=1, type=str)
def get(by_secs, key):
    while True:
        with interval(by_secs):
            value = source.get(key)
            click.echo(json.dumps(value))


if __name__ == '__main__':
    cli()
