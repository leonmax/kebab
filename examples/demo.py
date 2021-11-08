#!/usr/bin/env python
from pydantic import BaseModel, Field


class NestedConfig(BaseModel):
    name: str = "5"
    desc: str


class DemoConfig(BaseModel):
    ready: str = "5"
    int_value: str = Field(alias="int")
    nested: NestedConfig
