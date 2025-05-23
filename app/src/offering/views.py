import arrow
import pytz
import structlog
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.time_slot import TimeSlot
from offering.models import DailyOffering
from offering.serializers import OfferingPayloadItemSerializer, StoreOfferingResponseSerializer

log = structlog.get_logger("offering")


# Create your views here.


class StoreOfferingDataView(APIView):
    @swagger_auto_schema(
        operation_summary="Store Daily Offering Data",
        request_body=OfferingPayloadItemSerializer(many=True),
        responses={
            201: openapi.Response(description="Data stored successfully.", schema=StoreOfferingResponseSerializer),
            400: openapi.Response(description="Invalid input data."),
        },
        examples={
            "application/json": [
                {
                    "reference": "FI_client1_FCRN",
                    "unit": "MW",
                    "startTime": "2025-05-22T22:00:00Z",
                    "slotLength": 3600,
                    "values": [
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                        "1.0",
                    ],
                }
            ]
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = OfferingPayloadItemSerializer(data=request.data, many=True)
        trading_days = set()
        if not serializer.is_valid():
            return Response(
                {"error_details": serializer.errors, "error": "serialisation error"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not serializer.validated_data:
            return Response({"error": "Empty payload not allowed"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for item_data in serializer.validated_data:
                try:
                    trading_days |= self._process_offering_data(item_data)
                except ValueError as e:
                    log.error(e)
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"message": "Data stored successfully", "details": {"trading_days": sorted(trading_days)}},
            status=status.HTTP_201_CREATED,
        )

    def _process_offering_data(self, item_data):
        trading_days = set()
        start_time_cet = arrow.get(item_data["startTime"]).to(pytz.timezone("CET"))
        slot_length = item_data["slotLength"]
        values = item_data["values"]
        position_name = item_data["reference"]

        current_time = start_time_cet
        value_index = 0

        while value_index < len(values):
            current_date = current_time.date()
            trading_days.add(current_date)
            day_slot = TimeSlot.at(current_date, tz="CET")
            hours_in_day = len(day_slot.split(slot_length))

            if value_index + hours_in_day > len(values):
                raise ValueError(f"Not enough values for day {current_date}")

            day_values = values[value_index : value_index + hours_in_day]

            daily_offering, _ = DailyOffering.objects.get_or_create(position_name=position_name, date=current_date)

            daily_offering.add_entry(slot_length, day_values)

            value_index += hours_in_day
            current_time = current_time.shift(days=1).replace(hour=0, minute=0, second=0, microsecond=0)

        return trading_days
