import arrow
import pytz
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from offering.models import DailyOffering, DailyOfferingEntry
from offering.serializers import OfferingPayloadItemSerializer, StoreOfferingResponseSerializer


# Create your views here.

class StoreOfferingDataView(APIView):
    @swagger_auto_schema(
        operation_summary="Store Daily Offering Data",
        request_body=OfferingPayloadItemSerializer(many=True),
        responses={
            201: openapi.Response(description="Data stored successfully.", schema=StoreOfferingResponseSerializer),
            400: openapi.Response(description="Invalid input data.")
        },
        examples={
            "application/json": [
                {
                    "reference": "FI_client1_FCRN",
                    "unit": "MW",
                    "startTime": "2025-05-22T22:00:00Z",
                    "slotLength": 3600,
                    "values": [
                        "1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0",
                        "1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0"
                    ]
                }
            ]
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = OfferingPayloadItemSerializer(data=request.data, many=True)
        trading_days = []
        if serializer.is_valid():
            with transaction.atomic():
                for item_data in serializer.validated_data:
                    offering_date = arrow.get(item_data['startTime'], tzinfo=pytz.utc).to(pytz.timezone("CET")).date()
                    trading_days.append(offering_date)
                    position_name = item_data['reference']

                    daily_offering, _ = DailyOffering.objects.get_or_create(
                        position_name=position_name,
                        date=offering_date
                    )
                    try:
                        daily_offering.add_entry(item_data['slotLength'], item_data['values'])
                    except ValueError as e:
                        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Data stored successfully", "details": {"trading_days": trading_days}},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
