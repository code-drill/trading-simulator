from decimal import Decimal

import arrow
import pytz
from django.db import models

from common import const
from common.slot_length import SlotLength
from common.time_slot import TimeSlot


# Create your models here.

# #################################################################################
# we are trying to sell services for monday
# #################################################################################
# only one sale
# sunday
# R1 R2 R3 GC .... RE simulate_trading_on(R3)
# monday
# #################################################################################

# #################################################################################
# two sales on day -2, day -1
# friday
# R1, R2
# saturday
# R3 R4 R5 GC .... RE (22:20) simulate_trading_on(R5), RR1, RR2
#
# sunday
# RR3 RR4 RR5 GC .... RRE simulate_trading_on(R3), simulate_trading_on(RR3)
# #################################################################################


class DailyOfferingEntry(models.Model):
    slot_length = models.IntegerField(default=3600, choices=SlotLength.choices())
    values = models.JSONField()
    created_at = models.DateTimeField(default=lambda: arrow.now(pytz.timezone(const.trading_timezone_name)).datetime,
                                      editable=False)

    def __str__(self):
        return f"DailyOfferingEntry('{arrow.get(self.created_at).format('YYYY-MM-DD HH:mm:ss')}')"


class DailyOffering(models.Model):
    position_name = models.CharField(null=False, blank=False, max_length=100)
    date = models.DateField(null=False, blank=False)
    entries = models.ManyToManyField(DailyOfferingEntry)

    class Meta:
        ordering = ['date']
        indexes = [models.Index(fields=['date'])]

    def add_entry(self, slot_length: int, values: list[Decimal] | list[str]) -> DailyOfferingEntry:
        if slot_length not in dict(SlotLength.choices()).keys():
            raise ValueError(f"Slot length must be one of the following: {dict(SlotLength.choices()).keys()}")
        expected_values_count = len(TimeSlot.at(self.date, tz=const.trading_timezone_name).split(slot_length))
        received_values_count = len(values)
        if expected_values_count != received_values_count:
            raise ValueError(f"Values count should be: {expected_values_count}, but are: {received_values_count}")

        if self.pk is None:
            self.save()

        if isinstance(values[0], Decimal):
            values = [str(v) for v in values]

        entry = DailyOfferingEntry.objects.create(values=values, slot_length=slot_length)
        self.entries.add(entry)
        return entry

    def __str__(self):
        return f"{self.date} - {self.position_name}"
