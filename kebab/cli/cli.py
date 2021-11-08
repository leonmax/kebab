import importlib
import json
import logging
import sys
import time
from contextlib import contextmanager

import click

from kebab import load_source
from kebab.constants import DISABLE_RELOAD


@click.command()
@click.argument("sources", nargs=-1, type=str)
@click.option("--env-vars/--no-env-vars", default=False)
@click.option("-k", "--key", default=".", type=str)
@click.option("-m", "--model-class", type=str, help="a pydantic model class")
@click.option("-w", "--watch", default=DISABLE_RELOAD, type=float)
@click.option("-v", "--verbose", is_flag=True, default=False, type=bool)
def run(sources, key, watch, model_class, verbose, env_vars):
    if verbose:
        logging.basicConfig()
        logging.getLogger().level = logging.DEBUG
        logging.getLogger().propagate = True
    if not sources:
        sources = "app.yaml"
    conf = load_source(
        default_urls=sources,
        include_env_var=env_vars,
        reload_interval_in_secs=watch,
    )
    while True:
        with interval(watch):
            value = conf.get(key)
            if model_class:
                click.echo(_get_expected_type(model_class)(**value))
            else:
                click.echo(json.dumps(value))


def _get_expected_type(fully_qualified_path):
    (module_name, class_name) = fully_qualified_path.rsplit(".", 1)
    try:
        module = importlib.import_module(module_name)
        klass = getattr(module, class_name)
        return klass
    except ImportError:
        print(f"Module {module_name} does not exist")
        sys.exit(1)


@contextmanager
def interval(secs=DISABLE_RELOAD):
    try:
        yield
        if secs > 0:
            time.sleep(secs)
        else:
            sys.exit(0)
    except KeyboardInterrupt:
        raise


if __name__ == "__main__":
    run()
