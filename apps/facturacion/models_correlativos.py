from django.db import models

class CorrelativoFiscal(models.Model):
    TIPO_CHOICES = [
        ('factura', 'Factura'),
        ('control', 'Número de Control'),
        ('nota_entrega', 'Nota de Entrega'),
        ('presupuesto', 'Presupuesto/Pedido'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, unique=True)
    prefijo = models.CharField(max_length=10, blank=True)
    proximo_numero = models.PositiveIntegerField(default=1)
    longitud_ceros = models.PositiveIntegerField(default=6, help_text="Cantidad de ceros a la izquierda")
    
    def generar_siguiente(self):
        numero_formateado = str(self.proximo_numero).zfill(self.longitud_ceros)
        completo = f"{self.prefijo}{numero_formateado}"
        # No guardamos aquí para que el usuario decida cuándo avanzar
        return completo

    def avanzar(self):
        self.proximo_numero += 1
        self.save()

    class Meta:
        verbose_name = "Correlativo Fiscal"
        verbose_name_plural = "Correlativos Fiscales"

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.prefijo}{str(self.proximo_numero).zfill(self.longitud_ceros)}"
