from django.db import models


class FlowReading(models.Model):
    class Status(models.TextChoices):
        SECO = 'seco', 'Seco'
        NORMAL = 'normal', 'Normal'
        EXCESO = 'exceso', 'Exceso'
        ERROR = 'error', 'Error'
        DESCONECTADO = 'desconectado', 'Desconectado'

    class Source(models.TextChoices):
        ESP32 = 'ESP32', 'ESP32'
        SIMULACION = 'simulacion', 'Simulacion'

    sensor_id = models.CharField(max_length=80, default='entrada-principal')
    caudal_entrada = models.DecimalField(max_digits=8, decimal_places=2)
    caudal_salida1 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    caudal_salida2 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=Status.choices, default=Status.NORMAL)
    alerta = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    origen_dato = models.CharField(max_length=20, choices=Source.choices, default=Source.ESP32)
    observacion = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['sensor_id', '-fecha']),
            models.Index(fields=['estado', '-fecha']),
        ]

    def __str__(self):
        return f'{self.sensor_id} - {self.caudal_entrada} L/min - {self.estado}'
