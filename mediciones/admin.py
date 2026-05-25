from django.contrib import admin

from .models import FlowReading


@admin.register(FlowReading)
class FlowReadingAdmin(admin.ModelAdmin):
    list_display = ('sensor_id', 'caudal_entrada', 'estado', 'origen_dato', 'fecha')
    list_filter = ('estado', 'origen_dato', 'sensor_id')
    search_fields = ('sensor_id', 'observacion', 'alerta')
    readonly_fields = ('fecha',)
