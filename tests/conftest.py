import pytest

from kebab import DictSource, literal


@pytest.fixture
def source():
    return literal(
        key1="123",
        key2=2,
        key3=[3.0, 4.0, 5.0],
        key4={"nested": 1, "more": {"layer": "is better"}},
    )


@pytest.fixture
def context():
    return {
        "age": "123",
        "name": "today",
        "prof": {
            "level": 3.0,
            "title": "inside"
        }
    }


@pytest.fixture
def complex_source(context):
    return DictSource(context)
