from typing import Optional
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apis.models import DemoTable


class DemoTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoTable
        fields = ("record_id", "record_name")
        read_only_fields = ("record_id",)

    def create(self, validated_data):
        obj: Optional[DemoTable]
        try:
            obj = super().create(validated_data)
        except IntegrityError as e:
            if "unique constraint" in str(e.__cause__):
                record_name = validated_data.get("record_name", None)
                msg = "Unique data record ID already exists. " \
                      f"Cannot generate one for {record_name} "
                raise ValidationError({"detail": msg})
        return obj
