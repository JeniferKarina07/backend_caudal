from datetime import timedelta

from django.conf import settings
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone

from .models import FlowReading


def classify_flow(caudal_entrada):
    if caudal_entrada is None or caudal_entrada < 0:
        return FlowReading.Status.ERROR, 'Lectura invalida del sensor.'
    if caudal_entrada == 0:
        return FlowReading.Status.SECO, 'No se detecta flujo de agua.'
    if caudal_entrada > settings.CAUDAL_MAX_LPM:
        return FlowReading.Status.EXCESO, 'Caudal por encima del limite permitido.'
    return FlowReading.Status.NORMAL, ''


def create_flow_reading(validated_data):
    caudal_entrada = validated_data.get('caudal_entrada')
    estado, alerta = classify_flow(caudal_entrada)

    validated_data['estado'] = estado
    validated_data['alerta'] = alerta
    validated_data.setdefault('origen_dato', FlowReading.Source.ESP32)

    return FlowReading.objects.create(**validated_data)


def latest_status_payload():
    latest = FlowReading.objects.order_by('-fecha').first()
    if latest is None:
        return {
            'estado': FlowReading.Status.DESCONECTADO,
            'alerta': 'Aun no se han recibido lecturas.',
            'seconds_since_last_reading': None,
            'reading': None,
        }

    elapsed = timezone.now() - latest.fecha
    disconnected = elapsed > timedelta(seconds=settings.IOT_DISCONNECT_SECONDS)
    if disconnected:
        estado = FlowReading.Status.DESCONECTADO
        alerta = 'Sistema sin datos recientes del ESP32.'
    else:
        estado = latest.estado
        alerta = latest.alerta

    return {
        'estado': estado,
        'alerta': alerta,
        'seconds_since_last_reading': int(elapsed.total_seconds()),
        'reading': latest,
    }


def dashboard_payload():
    now = timezone.localtime()
    today = now.date()
    month_start = today.replace(day=1)

    latest_payload = latest_status_payload()
    daily_qs = FlowReading.objects.filter(fecha__date=today)
    monthly_qs = FlowReading.objects.filter(fecha__date__gte=month_start)
    recent_qs = FlowReading.objects.order_by('-fecha')[:30]
    alerts_qs = FlowReading.objects.exclude(alerta='').order_by('-fecha')[:10]

    return {
        'latest': latest_payload,
        'recent_readings': list(recent_qs),
        'active_alerts': list(alerts_qs),
        'stats': {
            'daily': aggregate_flow(daily_qs),
            'monthly': aggregate_flow(monthly_qs),
        },
        'config': {
            'caudal_max_lpm': settings.CAUDAL_MAX_LPM,
            'disconnect_seconds': settings.IOT_DISCONNECT_SECONDS,
            'polling_seconds': 3,
        },
    }


def aggregate_flow(queryset):
    data = queryset.aggregate(
        total=Count('id'),
        promedio=Avg('caudal_entrada'),
        maximo=Max('caudal_entrada'),
        minimo=Min('caudal_entrada'),
    )
    return {
        'total_lecturas': data['total'] or 0,
        'promedio_caudal': round(float(data['promedio'] or 0), 2),
        'maximo_caudal': round(float(data['maximo'] or 0), 2),
        'minimo_caudal': round(float(data['minimo'] or 0), 2),
    }
