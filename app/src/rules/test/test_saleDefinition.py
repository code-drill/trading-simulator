import datetime

import pytest
from assertpy import assert_that
from django.core.exceptions import ValidationError

from rules.models import SaleDefinition

pytestmark = pytest.mark.django_db


@pytest.fixture
def valid_sale_definition_data():
    return {
        "name": "Test Sale",
        "days_offset": 1,
        "gate_close_time": datetime.time(10, 0, 0),
        "result_time": datetime.time(11, 0, 0),
        "timezone_name": "CET",
    }


def test_clean_valid_data(valid_sale_definition_data):
    sale_def = SaleDefinition(**valid_sale_definition_data)
    sale_def.clean()


def test_clean_invalid_days_offset(valid_sale_definition_data):
    valid_sale_definition_data["days_offset"] = 0
    sale_def = SaleDefinition(**valid_sale_definition_data)
    with pytest.raises(ValidationError) as excinfo:
        sale_def.clean()
    assert_that(excinfo.value.messages).contains("days_offset must be greater than 0")


def test_clean_invalid_timezone_name(valid_sale_definition_data):
    valid_sale_definition_data["timezone_name"] = "Invalid/Timezone"
    sale_def = SaleDefinition(**valid_sale_definition_data)
    with pytest.raises(ValidationError) as excinfo:
        sale_def.clean()
    assert_that(excinfo.value.messages).contains("Unknown timezone: Invalid/Timezone")


def test_clean_result_time_not_greater_than_gate_close_time(valid_sale_definition_data):
    valid_sale_definition_data["result_time"] = datetime.time(9, 0, 0)
    sale_def = SaleDefinition(**valid_sale_definition_data)
    with pytest.raises(ValidationError) as excinfo:
        sale_def.clean()
    assert_that(excinfo.value.messages).contains("result_time must be greater than gate_close_time")


def test_clean_result_time_equal_to_gate_close_time(valid_sale_definition_data):
    valid_sale_definition_data["result_time"] = valid_sale_definition_data["gate_close_time"]
    sale_def = SaleDefinition(**valid_sale_definition_data)
    with pytest.raises(ValidationError) as excinfo:
        sale_def.clean()
    assert_that(excinfo.value.messages).contains("result_time must be greater than gate_close_time")
