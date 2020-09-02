import json
import time

import click

from kebab import load_source
from kebab.sources import _DISABLE_RELOAD

DISABLE_RELOAD = _DISABLE_RELOAD


@click.command()
@click.argument("sources", nargs=-1, type=str)
@click.option("--env-vars/--no-env-vars", default=False)
@click.option("-k", "--key", default=".", type=str)
@click.option("-w", "--watch", default=DISABLE_RELOAD, type=float)
def run(sources, key, watch, env_vars):
    if not sources:
        sources = "app.yaml"
    conf = load_source(
        default_urls=sources,
        include_env_var=env_vars,
        reload_interval_in_secs=watch,
    )
    while True:
        click.echo(json.dumps(conf.get(key)))
        if watch == DISABLE_RELOAD:
            break
        time.sleep(watch)


if __name__ == "__main__":
    run()
