from django.db import models
from django.conf import settings
from decimal import Decimal

class SolicitudViatico(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('liquidada', 'Liquidada'),
    ]
    
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes_viaticos')
    destino = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField()
    monto_solicitado = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    aprobado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='aprobaciones_viaticos')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Viático {self.solicitante} - {self.destino}"

    @property
    def total_gastado(self):
        return sum(gasto.monto for gasto in self.gastos.all())

    @property
    def saldo(self):
        return self.monto_solicitado - self.total_gastado

class GastoViatico(models.Model):
    TIPOS = [
        ('alojamiento', 'Alojamiento'),
        ('alimentacion', 'Alimentación'),
        ('transporte', 'Transporte'),
        ('combustible', 'Combustible'),
        ('otros', 'Otros'),
    ]
    
    solicitud = models.ForeignKey(SolicitudViatico, on_delete=models.CASCADE, related_name='gastos')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.CharField(max_length=200)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    comprobante = models.FileField(upload_to='comprobantes_viaticos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.descripcion} - {self.monto}"