import pytest
import time_machine
from assertpy import assert_that
from rest_framework import status
from rest_framework.test import APIClient

from offering.models import DailyOffering

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def url():
    return "/api/offering/upload/"


def test_normal_day_24_hours(api_client, url):
    payload = [{
        "reference": "FI_client1_FCRN",
        "unit": "MW",
        "startTime": "2025-01-15T23:00:00Z",
        "slotLength": 3600,
        "values": ["1.0"] * 24
    }]

    response = api_client.post(url, data=payload, format='json')

    assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
    assert_that(DailyOffering.objects.count()).is_equal_to(1)

    offering = DailyOffering.objects.first()
    assert_that(offering.position_name).is_equal_to("FI_client1_FCRN")
    assert_that(str(offering.date)).is_equal_to("2025-01-16")
    assert_that(offering.entries.count()).is_equal_to(1)
    assert_that(offering.entries.first().values).is_length(24)


@time_machine.travel("2024-03-31 12:00:00", tick=False)
def test_switch_to_summer_time_23_hours(api_client, url):
    payload = [{
        "reference": "FI_client1_FCRN",
        "unit": "MW",
        "startTime": "2024-03-30T23:00:00Z",
        "slotLength": 3600,
        "values": ["1.0"] * 23
    }]

    response = api_client.post(url, data=payload, format='json')

    assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
    assert_that(DailyOffering.objects.count()).is_equal_to(1)

    offering = DailyOffering.objects.first()
    assert_that(str(offering.date)).is_equal_to("2024-03-31")
    assert_that(offering.entries.first().values).is_length(23)


@time_machine.travel("2024-10-27 12:00:00", tick=False)
def test_switch_to_winter_time_25_hours(api_client, url):
    payload = [{
        "reference": "FI_client1_FCRN",
        "unit": "MW",
        "startTime": "2024-10-26T22:00:00Z",
        "slotLength": 3600,
        "values": ["1.0"] * 25
    }]

    response = api_client.post(url, data=payload, format='json')

    assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
    assert_that(DailyOffering.objects.count()).is_equal_to(1)

    offering = DailyOffering.objects.first()
    assert_that(str(offering.date)).is_equal_to("2024-10-27")
    assert_that(offering.entries.first().values).is_length(25)


def test_two_normal_days_48_hours(api_client, url):
    payload = [{
        "reference": "FI_client1_FCRN",
        "unit": "MW",
        "startTime": "2025-01-15T23:00:00Z",
        "slotLength": 3600,
        "values": ["1.0"] * 48
    }]

    response = api_client.post(url, data=payload, format='json')

    assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
    assert_that(DailyOffering.objects.count()).is_equal_to(2)

    offerings = DailyOffering.objects.order_by('date')
    assert_that(str(offerings[0].date)).is_equal_to("2025-01-16")
    assert_that(str(offerings[1].date)).is_equal_to("2025-01-17")
    assert_that(offerings[0].entries.first().values).is_length(24)
    assert_that(offerings[1].entries.first().values).is_length(24)


@time_machine.travel("2024-03-31 12:00:00", tick=False)
def test_two_days_with_summer_time_switch_47_hours(api_client, url):
    payload = [{
        "reference": "FI_client1_FCRN",
        "unit": "MW",
        "startTime": "2024-03-30T23:00:00Z",
        "slotLength": 3600,
        "values": ["1.0"] * 47
    }]

    response = api_client.post(url, data=payload, format='json')

    assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
    assert_that(DailyOffering.objects.count()).is_equal_to(2)

    offerings = DailyOffering.objects.order_by('date')
    assert_that(str(offerings[0].date)).is_equal_to("2024-03-31")
    assert_that(str(offerings[1].date)).is_equal_to("2024-04-01")
    assert_that(offerings[0].entries.first().values).is_length(23)
    assert_that(offerings[1].entries.first().values).is_length(24)


@time_machine.travel("2024-10-27 12:00:00", tick=False)
def test_two_days_with_winter_time_switch_49_hours(api_client, url):
    payload = [{
        "reference": "FI_client1_FCRN",
        "unit": "MW",
        "startTime": "2024-10-26T22:00:00Z",
        "slotLength": 3600,
        "values": ["1.0"] * 49
    }]

    response = api_client.post(url, data=payload, format='json')

    assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
    assert_that(DailyOffering.objects.count()).is_equal_to(2)

    offerings = DailyOffering.objects.order_by('date')
    assert_that(str(offerings[0].date)).is_equal_to("2024-10-27")
    assert_that(str(offerings[1].date)).is_equal_to("2024-10-28")
    assert_that(offerings[0].entries.first().values).is_length(25)
    assert_that(offerings[1].entries.first().values).is_length(24)


def test_multiple_payloads_same_day(api_client, url):
    payload = [
        {
            "reference": "FI_client1_FCRN",
            "unit": "MW",
            "startTime": "2025-01-15T23:00:00Z",
            "slotLength": 3600,
            "values": ["1.0"] * 24
        },
        {
            "reference": "FI_client2_FCRN",
            "unit": "MW",
            "startTime": "2025-01-15T23:00:00Z",
            "slotLength": 3600,
            "values": ["2.0"] * 24
        }
    ]

    response = api_client.post(url, data=payload, format='json')

    assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
    assert_that(DailyOffering.objects.count()).is_equal_to(2)

    offering1 = DailyOffering.objects.get(position_name="FI_client1_FCRN")
    offering2 = DailyOffering.objects.get(position_name="FI_client2_FCRN")
    assert_that(offering1.entries.first().values).contains_only("1.0")
    assert_that(offering2.entries.first().values).contains_only("2.0")


def test_invalid_values_count_returns_error(api_client, url):
    payload = [{
        "reference": "FI_client1_FCRN",
        "unit": "MW",
        "startTime": "2025-01-15T23:00:00Z",
        "slotLength": 3600,
        "values": ["1.0"] * 10
    }]

    response = api_client.post(url, data=payload, format='json')

    assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
    assert_that(response.data).contains_key("error")


def test_invalid_slot_length_returns_error(api_client, url):
    payload = [{
        "reference": "FI_client1_FCRN",
        "unit": "MW",
        "startTime": "2025-01-15T23:00:00Z",
        "slotLength": 1234,
        "values": ["1.0"] * 24
    }]

    response = api_client.post(url, data=payload, format='json')

    assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
    assert_that(response.data).contains_key("error")


def test_missing_required_fields_returns_validation_error(api_client, url):
    payload = [{
        "reference": "FI_client1_FCRN",
        "unit": "MW"
    }]

    response = api_client.post(url, data=payload, format='json')

    assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
    assert_that(response.data[0]).contains_key("startTime")
    assert_that(response.data[0]).contains_key("slotLength")
    assert_that(response.data[0]).contains_key("values")


def test_empty_payload_returns_validation_error(api_client, url):
    payload = []

    response = api_client.post(url, data=payload, format='json')

    assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
