import pytz
from django.core.exceptions import ValidationError
from django.db import models

from common.const import trading_timezone_name


# Create your models here.

class Market(models.Model):
    code = models.CharField(max_length=20, unique=True, primary_key=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Market"
        verbose_name_plural = "Markets"


class SaleDefinition(models.Model):
    name = models.CharField(max_length=100)
    days_offset = models.IntegerField(default=1)
    gate_close_time = models.TimeField()
    result_time = models.TimeField()
    timezone_name = models.CharField(max_length=100, default=trading_timezone_name)

    def clean(self):
        if self.days_offset < 1:
            raise ValidationError("days_offset must be greater than 0")

        try:
            pytz.timezone(self.timezone_name)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValidationError(f"Unknown timezone: {self.timezone_name}")

        if self.result_time <= self.gate_close_time:
            raise ValidationError("result_time must be greater than gate_close_time")

    def __str__(self):
        return self.name

