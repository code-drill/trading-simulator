import pytest
from decimal import Decimal
from datetime import date
import time_machine
from assertpy import assert_that

from offering.models import DailyOffering


@pytest.mark.django_db
class TestDailyOffering:

    def test_add_entry_saves_model_if_not_persisted(self):
        offering = DailyOffering(position_name="Test Position", date=date(2024, 1, 15))
        values = ["10.5"] * 24

        offering.add_entry(3600, values)

        assert_that(offering.pk).is_not_none()

    def test_add_entry_with_decimal_values_converts_to_strings(self):
        offering = DailyOffering.objects.create(position_name="Test Position", date=date(2024, 1, 15))
        decimal_values = [Decimal("10.5")] * 24

        entry = offering.add_entry(3600, decimal_values)

        assert_that(entry.values).contains_only("10.5")

    def test_add_entry_with_string_values(self):
        offering = DailyOffering.objects.create(position_name="Test Position", date=date(2024, 1, 15))
        string_values = ["10.5"] * 24

        entry = offering.add_entry(3600, string_values)

        assert_that(entry.values).is_equal_to(string_values)

    def test_add_entry_invalid_slot_length_raises_error(self):
        offering = DailyOffering(position_name="Test Position", date=date(2024, 1, 15))
        values = ["10.5"] * 24

        with pytest.raises(ValueError, match="Slot length must be one of the following"):
            offering.add_entry(1234, values)

    def test_add_entry_wrong_values_count_raises_error(self):
        offering = DailyOffering(position_name="Test Position", date=date(2024, 1, 15))
        values = ["10.5"] * 10

        with pytest.raises(ValueError, match="Values count should be: 24, but are: 10"):
            offering.add_entry(3600, values)

    def test_add_entry_creates_and_links_entry(self):
        offering = DailyOffering.objects.create(position_name="Test Position", date=date(2024, 1, 15))
        values = ["10.5"] * 24

        entry = offering.add_entry(3600, values)

        assert_that(offering.entries.filter(pk=entry.pk)).is_length(1)
        assert_that(entry.slot_length).is_equal_to(3600)
        assert_that(entry.values).is_equal_to(values)

    @time_machine.travel("2024-03-31 12:00:00", tick=False)
    def test_add_entry_dst_transition_23_hours(self):
        offering = DailyOffering.objects.create(position_name="Test Position", date=date(2024, 3, 31))
        values = ["10.5"] * 23

        entry = offering.add_entry(3600, values)

        assert_that(entry.values).is_length(23)
        assert_that(offering.entries.filter(pk=entry.pk)).is_length(1)

    @time_machine.travel("2024-10-27 12:00:00", tick=False)
    def test_add_entry_dst_transition_25_hours(self):
        offering = DailyOffering.objects.create(position_name="Test Position", date=date(2024, 10, 27))
        values = ["10.5"] * 25

        entry = offering.add_entry(3600, values)

        assert_that(entry.values).is_length(25)
        assert_that(offering.entries.filter(pk=entry.pk)).is_length(1)

    @time_machine.travel("2024-03-31 12:00:00", tick=False)
    def test_add_entry_dst_transition_23_hours_wrong_count_raises_error(self):
        offering = DailyOffering.objects.create(position_name="Test Position", date=date(2024, 3, 31))
        values = ["10.5"] * 24

        with pytest.raises(ValueError, match="Values count should be: 23, but are: 24"):
            offering.add_entry(3600, values)

    @time_machine.travel("2024-10-27 12:00:00", tick=False)
    def test_add_entry_dst_transition_25_hours_wrong_count_raises_error(self):
        offering = DailyOffering.objects.create(position_name="Test Position", date=date(2024, 10, 27))
        values = ["10.5"] * 24

        with pytest.raises(ValueError, match="Values count should be: 25, but are: 24"):
            offering.add_entry(3600, values)