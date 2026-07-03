from django.db import models

class ActivoFijo(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    fecha_adquisicion = models.DateField()
    valor_compra = models.DecimalField(max_digits=12, decimal_places=2)
    vida_util_meses = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        verbose_name = 'Activo Fijo'
        verbose_name_plural = 'Activos Fijos'