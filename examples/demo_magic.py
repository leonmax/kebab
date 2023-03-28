#!/usr/bin/env python
from kebab import config, Field


@config(auto_repr=True)
class DemoConfig:
    str_value = Field("ready", default="5", expected_type=str)
    int_value = Field("int", required=True, expected_type=int, masked=True)
