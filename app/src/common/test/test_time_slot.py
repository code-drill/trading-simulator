from datetime import timedelta

import arrow
import pytest
import pytz
from arrow import Arrow
from assertpy import assert_that

from common.time_slot import TimeSlot


def test_create_daily_time_slot_at_utc() -> None:
    specific_day = TimeSlot.at(2023, 1, 15)

    assert specific_day.from_date == Arrow(2023, 1, 15, 0, 0, 0, tzinfo=pytz.timezone("CET"))
    assert specific_day.to_date == Arrow(2023, 1, 16, 0, 0, 0, tzinfo=pytz.timezone("CET"))


def test_one_slot_within_another() -> None:
    slot1 = TimeSlot(
        from_date=Arrow(2023, 1, 2, 0, 0, 0, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2023, 1, 2, 23, 59, 59, tzinfo=pytz.timezone("CET")),
    )
    slot2 = TimeSlot(
        from_date=Arrow(2023, 1, 1, 0, 0, 0, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2023, 1, 3, 0, 0, 0, tzinfo=pytz.timezone("CET")),
    )

    assert slot1.within(slot2)
    assert not slot2.within(slot1)


def test_one_slot_is_not_within_another_if_they_just_overlap() -> None:
    slot1 = TimeSlot(
        from_date=Arrow(2023, 1, 1, 0, 0, 0, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2023, 1, 2, 23, 59, 59, tzinfo=pytz.timezone("CET")),
    )
    slot2 = TimeSlot(
        from_date=Arrow(2023, 1, 2, 0, 0, 0, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2023, 1, 3, 0, 0, 0, tzinfo=pytz.timezone("CET")),
    )

    assert not slot1.within(slot2)
    assert not slot2.within(slot1)

    slot3 = TimeSlot(
        from_date=Arrow(2023, 1, 2, 0, 0, 0, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2023, 1, 3, 23, 59, 59, tzinfo=pytz.timezone("CET")),
    )
    slot4 = TimeSlot(
        from_date=Arrow(2023, 1, 1, 0, 0, 0, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2023, 1, 2, 23, 59, 59, tzinfo=pytz.timezone("CET")),
    )

    assert not slot3.within(slot4)
    assert not slot4.within(slot3)


def test_slot_is_not_within_another_when_they_are_completely_outside() -> None:
    slot1 = TimeSlot(
        from_date=Arrow(2023, 1, 1, 0, 0, 0, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2023, 1, 1, 23, 59, 59, tzinfo=pytz.timezone("CET")),
    )
    slot2 = TimeSlot(
        from_date=Arrow(2023, 1, 2, 0, 0, 0, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2023, 1, 3, 0, 0, 0, tzinfo=pytz.timezone("CET")),
    )

    assert not slot1.within(slot2)
    assert not slot2.within(slot1)


def test_slot_is_within_itself() -> None:
    slot1 = TimeSlot(
        from_date=Arrow(2023, 1, 1, 0, 0, 0, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2023, 1, 1, 23, 59, 59, tzinfo=pytz.timezone("CET")),
    )

    assert slot1.within(slot1)


def test_slot_overlaps() -> None:
    slot_1 = TimeSlot(
        from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
    )
    slot_2 = TimeSlot(
        from_date=Arrow(2022, 1, 5, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 15, tzinfo=pytz.timezone("CET")),
    )
    slot_3 = TimeSlot(
        from_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
    )
    slot_4 = TimeSlot(
        from_date=Arrow(2022, 1, 5, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
    )
    slot_5 = TimeSlot(
        from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
    )

    assert slot_1.overlaps(slot_2)
    assert slot_1.overlaps(slot_1)
    assert slot_1.overlaps(slot_3)
    assert slot_1.overlaps(slot_4)
    assert slot_1.overlaps(slot_5)


def test_slot_not_overlaps() -> None:
    slot_1 = TimeSlot(
        from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
    )
    slot_2 = TimeSlot(
        from_date=Arrow(2022, 1, 10, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
    )
    slot_3 = TimeSlot(
        from_date=Arrow(2022, 1, 11, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
    )

    assert not slot_1.overlaps(slot_2)
    assert not slot_1.overlaps(slot_3)


def test_removing_common_parts_has_no_effect_when_there_is_no_overlap() -> None:
    slot_1 = TimeSlot(
        from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
    )
    slot_2 = TimeSlot(
        from_date=Arrow(2022, 1, 15, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
    )

    assert slot_1.leftover_after_removing_common_with(slot_2) == [slot_1, slot_2]


def test_removing_common_parts_when_there_is_full_overlap() -> None:
    slot_1 = TimeSlot(
        from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
    )

    assert slot_1.leftover_after_removing_common_with(slot_1) == []


def test_removing_common_parts_when_there_is_some_overlap() -> None:
    slot_1 = TimeSlot(
        from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 15, tzinfo=pytz.timezone("CET")),
    )
    slot_2 = TimeSlot(
        from_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
    )

    difference = slot_1.leftover_after_removing_common_with(slot_2)

    assert difference == [
        TimeSlot(
            from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
            to_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
        ),
        TimeSlot(
            from_date=Arrow(2022, 1, 15, tzinfo=pytz.timezone("CET")),
            to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
        ),
    ]

    slot_3 = TimeSlot(
        from_date=Arrow(2022, 1, 5, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
    )
    slot_4 = TimeSlot(
        from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
    )

    difference2 = slot_3.leftover_after_removing_common_with(slot_4)

    assert difference2 == [
        TimeSlot(
            from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
            to_date=Arrow(2022, 1, 5, tzinfo=pytz.timezone("CET")),
        ),
        TimeSlot(
            from_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
            to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
        ),
    ]


def test_removing_common_parts_when_one_slot_is_fully_within_another() -> None:
    slot_1 = TimeSlot(
        from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
    )
    slot_2 = TimeSlot(
        from_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 15, tzinfo=pytz.timezone("CET")),
    )

    difference = slot_1.leftover_after_removing_common_with(slot_2)

    assert difference == [
        TimeSlot(
            from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
            to_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
        ),
        TimeSlot(
            from_date=Arrow(2022, 1, 15, tzinfo=pytz.timezone("CET")),
            to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
        ),
    ]


def test_two_slots_have_common_part_when_overlap() -> None:
    slot_1 = TimeSlot(
        from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 15, tzinfo=pytz.timezone("CET")),
    )
    slot_2 = TimeSlot(
        from_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
    )

    common = slot_1.common_part_with(slot_2)

    assert not common.is_empty()
    assert common == TimeSlot(
        from_date=Arrow(2022, 1, 10, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 15, tzinfo=pytz.timezone("CET")),
    )


def test_two_slots_have_common_part_when_full_overlap() -> None:
    slot_1 = TimeSlot(
        from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
    )
    slot_2 = TimeSlot(
        from_date=Arrow(2022, 1, 1, tzinfo=pytz.timezone("CET")),
        to_date=Arrow(2022, 1, 20, tzinfo=pytz.timezone("CET")),
    )

    common = slot_1.common_part_with(slot_2)

    assert not common.is_empty()
    assert slot_1 == common


def test_split_equal_duration():
    slot = TimeSlot(arrow.get("2024-01-01T00:00:00"), arrow.get("2024-01-01T04:00:00"))
    result = slot.split(timedelta(hours=2))

    assert_that(result).is_length(2)
    assert_that(result[0].from_date).is_equal_to(arrow.get("2024-01-01T00:00:00"))
    assert_that(result[0].to_date).is_equal_to(arrow.get("2024-01-01T02:00:00"))
    assert_that(result[1].from_date).is_equal_to(arrow.get("2024-01-01T02:00:00"))
    assert_that(result[1].to_date).is_equal_to(arrow.get("2024-01-01T04:00:00"))


def test_split_with_int_seconds():
    slot = TimeSlot(arrow.get("2024-01-01T00:00:00"), arrow.get("2024-01-01T00:02:00"))
    result = slot.split(60)

    assert_that(result).is_length(2)
    assert_that(result[0].duration).is_equal_to(timedelta(minutes=1))
    assert_that(result[1].duration).is_equal_to(timedelta(minutes=1))


def test_split_single_slot():
    slot = TimeSlot(arrow.get("2024-01-01T00:00:00"), arrow.get("2024-01-01T01:00:00"))
    result = slot.split(timedelta(hours=1))

    assert_that(result).is_length(1)
    assert_that(result[0]).is_equal_to(slot)


def test_split_not_divisible_raises_error():
    slot = TimeSlot(arrow.get("2024-01-01T00:00:00"), arrow.get("2024-01-01T01:30:00"))

    with pytest.raises(ValueError, match="Slot duration not divisible by split duration"):
        slot.split(timedelta(hours=1))


def test_split_empty_slot():
    slot = TimeSlot.empty()
    result = slot.split(timedelta(hours=1))

    assert_that(result).is_empty()


def test_split_multiple_parts():
    slot = TimeSlot(arrow.get("2024-01-01T00:00:00"), arrow.get("2024-01-01T06:00:00"))
    result = slot.split(timedelta(hours=1))

    assert_that(result).is_length(6)
    for i, time_slot in enumerate(result):
        expected_start = arrow.get("2024-01-01T00:00:00").shift(hours=i)
        expected_end = arrow.get("2024-01-01T00:00:00").shift(hours=i + 1)
        assert_that(time_slot.from_date).is_equal_to(expected_start)
        assert_that(time_slot.to_date).is_equal_to(expected_end)
