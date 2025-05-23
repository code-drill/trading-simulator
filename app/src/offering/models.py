import arrow
import pytz
from django.db import models

from common import const
from common.slot_length import SlotLength


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
