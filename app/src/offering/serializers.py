from rest_framework import serializers

from common.slot_length import SlotLength


class OfferingPayloadItemSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=100)
    unit = serializers.CharField(max_length=10, required=False)
    startTime = serializers.DateTimeField()
    slotLength = serializers.ChoiceField(choices=[c[0] for c in SlotLength.choices()])
    values = serializers.ListField(child=serializers.CharField())

class StoredOfferingDetailsSerializer(serializers.Serializer):
    trading_days = serializers.ListField(child=serializers.DateField())

class StoreOfferingResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    details = StoredOfferingDetailsSerializer()