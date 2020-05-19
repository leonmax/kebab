import click
import json

from kebab.sources import load_source


@click.command()
@click.argument('sources', nargs=-1, type=str)
@click.option('--env-vars/--no-env-vars', default=False)
@click.option('-k', '--key', default='.', type=str)
def run(sources, key, env_vars):
    conf = load_source(default_urls=sources, include_env_var=env_vars)
    click.echo(json.dumps(conf.get(key)))
