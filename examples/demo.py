import json

import click

from examples.util import by_interval
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
@click.option('-i', '--interval', default=-1, type=float)
def cast(interval):
    while True:
        with by_interval(interval):
            value = source.cast("demo", DemoConfig)
            click.echo(value)


@cli.command()
@click.option('-i', '--interval', default=-1, type=float)
@click.argument('key', default='.', nargs=1, type=str)
def get(interval, key):
    while True:
        with by_interval(interval):
            value = source.get(key)
            click.echo(json.dumps(value))


if __name__ == '__main__':
    cli()
