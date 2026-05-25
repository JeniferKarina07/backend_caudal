from rest_framework import serializers

from .models import FlowReading
from .services import create_flow_reading


class FlowReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowReading
        fields = [
            'id',
            'sensor_id',
            'caudal_entrada',
            'caudal_salida1',
            'caudal_salida2',
            'estado',
            'alerta',
            'fecha',
            'origen_dato',
            'observacion',
        ]
        read_only_fields = ['id', 'estado', 'alerta', 'fecha']

    def validate_caudal_entrada(self, value):
        if value is None:
            raise serializers.ValidationError('El caudal de entrada es obligatorio.')
        return value

    def create(self, validated_data):
        return create_flow_reading(validated_data)


class FlowReadingReadSerializer(FlowReadingSerializer):
    fuga_estimada = serializers.SerializerMethodField()

    class Meta(FlowReadingSerializer.Meta):
        fields = FlowReadingSerializer.Meta.fields + ['fuga_estimada']

    def get_fuga_estimada(self, obj):
        if obj.caudal_salida1 is None or obj.caudal_salida2 is None:
            return None
        return float(obj.caudal_entrada - (obj.caudal_salida1 + obj.caudal_salida2))
