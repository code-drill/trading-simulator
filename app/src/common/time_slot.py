from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import singledispatchmethod

import arrow
import pytz
from arrow import Arrow


@dataclass(frozen=True)
class TimeSlot:
    from_date: Arrow
    to_date: Arrow

    @staticmethod
    def empty() -> TimeSlot:
        return TimeSlot(Arrow.min, Arrow.min)

    @singledispatchmethod
    @classmethod
    def at(cls, from_day: date | int, tz: str | datetime.tzinfo, to_day_exclusive: date | None = None) -> TimeSlot:
        raise NotImplementedError


    @at.register(int)
    @classmethod
    def _(cls, year: int, month: int = 1, day: int = 1, tz: str | datetime.tzinfo = "CET") -> TimeSlot:
        return TimeSlot.at(datetime(year, month, day), tz)

    @at.register(date)
    @classmethod
    def _(cls, from_day: date, tz: str | datetime.tzinfo, to_day_exclusive: date | None = None) -> TimeSlot:
        if isinstance(tz, str):
            tz = pytz.timezone(tz)
        if to_day_exclusive is None:
            to_day_exclusive = arrow.get(from_day, tzinfo=tz).shift(days=1).floor("day")
        if isinstance(to_day_exclusive, date):
            to_day_exclusive = arrow.get(to_day_exclusive, tzinfo=tz).floor("day")

        start_day = arrow.get(from_day, tzinfo=tz)

        return cls(start_day, to_day_exclusive)

    def within(self, other: TimeSlot) -> bool:
        return not self.from_date < other.from_date and not self.to_date > other.to_date

    def overlaps(self, other: TimeSlot) -> bool:
        return self.from_date <= other.to_date and self.to_date >= other.from_date

    def leftover_after_removing_common_with(self, other: TimeSlot) -> list[TimeSlot]:
        result: list[TimeSlot] = []
        if self == other:
            return []
        if not other.overlaps(self):
            return [self, other]
        if self.from_date < other.from_date:
            result.append(TimeSlot(self.from_date, other.from_date))
        elif other.from_date < self.from_date:
            result.append(TimeSlot(other.from_date, self.from_date))
        if self.to_date > other.to_date:
            result.append(TimeSlot(other.to_date, self.to_date))
        elif other.to_date > self.to_date:
            result.append(TimeSlot(self.to_date, other.to_date))
        return result

    def is_empty(self) -> bool:
        return self.from_date == self.to_date

    def common_part_with(self, other: TimeSlot) -> TimeSlot:
        if not self.overlaps(other):
            return TimeSlot(self.from_date, self.from_date)
        return TimeSlot(max(self.from_date, other.from_date), min(self.to_date, other.to_date))

    @property
    def duration(self) -> timedelta:
        return self.to_date - self.from_date

    def split(self, duration: timedelta | int) -> list[TimeSlot]:
        if isinstance(duration, int):
            duration = timedelta(seconds=duration)

        total_duration = self.duration
        if total_duration.total_seconds() % duration.total_seconds() != 0:
            raise ValueError("Slot duration not divisible by split duration")

        slots = []
        current = self.from_date

        while current < self.to_date:
            next_time = current.shift(seconds=duration.total_seconds())
            slots.append(TimeSlot(current, next_time))
            current = next_time

        return slots