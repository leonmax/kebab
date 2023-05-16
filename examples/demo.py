#!/usr/bin/env python
from pydantic import BaseModel, Field
from kebab import load_source
import logging
import logging.config
import time


class NestedConfig(BaseModel):
    name: str = "5"
    desc: str


class DemoConfig(BaseModel):
    ready: str = "5"
    int_value: str = Field(alias="int")
    nested: NestedConfig


if __name__ == "__main__":
    src = load_source("app.yaml")
    _log = logging.getLogger(__name__)
    logging.basicConfig()

    while True:
        logging.config.dictConfig(src.get('logging'))
        config = src.get('demo', expected_type=DemoConfig)
        _log.info(config)
        time.sleep(1)

