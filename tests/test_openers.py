import os
import sys

import pytest

from kebab.openers import DEFAULT_OPENER, add_aws_handlers

try:
    # noinspection PyUnresolvedReferences
    import boto3  # noqa: F401

    # noinspection PyUnresolvedReferences
    from kebab.aws import S3Handler
except ImportError:
    pytest.skip(
        "Failed to import boto3 and S3Handler, will skip aws test",
        allow_module_level=True,
    )


@pytest.fixture
def opener():
    return DEFAULT_OPENER


def test_python_path(opener):
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

    result = opener.open("pythonpath:data/conf1.yaml").read()
    assert result.strip() == "string_field: better value"


def test_default_opener_without_s3():
    """Test that DEFAULT_OPENER does not include S3Handler by default"""
    handler_classes = [handler.__class__ for handler in DEFAULT_OPENER.handlers]
    assert S3Handler not in handler_classes


def test_add_s3_handler():
    """Test that add_s3_handlers properly adds the S3Handler"""
    # Call add_s3_handlers
    add_aws_handlers(DEFAULT_OPENER)

    # Verify S3Handler is now in the handlers
    handler_classes = [handler.__class__ for handler in DEFAULT_OPENER.handlers]
    assert S3Handler in handler_classes
