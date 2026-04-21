from django.db import models
import os

class ConfiguracionEmpresa(models.Model):
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=20, verbose_name="NIT/RUT")
    direccion = models.TextField()
    telefono = models.CharField(max_length=50)
    email = models.EmailField()
    logo = models.ImageField(upload_to='empresa/', null=True, blank=True)
    moneda = models.CharField(max_length=10, default='$')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Configuración de Empresa"
        verbose_name_plural = "Configuraciones de Empresa"

class RegistroRespaldo(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to='backups/')
    exitoso = models.BooleanField(default=True)
    tamano_mb = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"Respaldo - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Registro de Respaldo"
        verbose_name_plural = "Registros de Respaldos"