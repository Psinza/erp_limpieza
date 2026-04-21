from django.db import models
from datetime import date

class ActivoFijo(models.Model):
    METODOS_DEPRECIACION = [
        ('lineal', 'Líneal'),
        ('decremento', 'Decremento Doble'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
    fecha_adquisicion = models.DateField()
    valor_compra = models.DecimalField(max_digits=12, decimal_places=2)
    valor_residual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vida_util_anios = models.PositiveIntegerField(default=5)
    metodo_depreciacion = models.CharField(max_length=20, choices=METODOS_DEPRECIACION, default='lineal')
    estado = models.CharField(max_length=50, default='Operativo')
    ubicacion = models.CharField(max_length=200, blank=True)
    responsable = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def depreciacion_anual(self):
        if self.metodo_depreciacion == 'lineal':
            return (self.valor_compra - self.valor_residual) / self.vida_util_anios
        elif self.metodo_depreciacion == 'decremento':
            return (self.valor_compra - self.depreciacion_acumulada) * 2 / self.vida_util_anios
        return 0
    
    @property
    def depreciacion_acumulada(self):
        from dateutil.relativedelta import relativedelta
        anios_transcurridos = (date.today() - self.fecha_adquisicion).days / 365.25
        if anios_transcurridos <= 0:
            return 0
        if self.metodo_depreciacion == 'lineal':
            return min(self.depreciacion_anual * anios_transcurridos, self.valor_compra - self.valor_residual)
        elif self.metodo_depreciacion == 'decremento':
            # Cálculo simplificado para decremento doble
            tasa = 2 / self.vida_util_anios
            acumulada = 0
            valor_libro = self.valor_compra
            for _ in range(int(anios_transcurridos)):
                dep = valor_libro * tasa
                acumulada += dep
                valor_libro -= dep
                if valor_libro <= self.valor_residual:
                    acumulada = self.valor_compra - self.valor_residual
                    break
            return min(acumulada, self.valor_compra - self.valor_residual)
        return 0
    
    @property
    def valor_libro(self):
        return self.valor_compra - self.depreciacion_acumulada