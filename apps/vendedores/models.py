from django.db import models
from django.conf import settings

class Vendedor(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    codigo_empleado = models.CharField(max_length=20, unique=True)
    comision_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    meta_mensual = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.get_full_name()} ({self.codigo_empleado})"

class Comision(models.Model):
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name='comisiones')
    pedido_venta = models.ForeignKey('ventas.Pedido', on_delete=models.CASCADE)
    monto_comision = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_calculo = models.DateTimeField(auto_now_add=True)
    pagado = models.BooleanField(default=False)