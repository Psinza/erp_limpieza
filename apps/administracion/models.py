from django.db import models
from django.conf import settings

class Empresa(models.Model):
    nombre = models.CharField(max_length=200)
    rif = models.CharField(max_length=20, verbose_name="RIF / NIT")
    direccion = models.TextField()
    telefono = models.CharField(max_length=50)
    email = models.EmailField()
    logo = models.ImageField(upload_to='empresa/', null=True, blank=True)
    moneda_simbolo = models.CharField(max_length=5, default='$')

    class Meta:
        verbose_name = "Configuración de Empresa"
        verbose_name_plural = "Configuración de Empresa"

    def __str__(self):
        return self.nombre

class RegistroRespaldo(models.Model):
    nombre_original = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='backups/', null=True, blank=True)
    tamano_mb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exitoso = models.BooleanField(default=True)
    error_log = models.TextField(null=True, blank=True)
    
    # Campos de Auditoría
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='respaldos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='respaldos_modificados')
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registro de Respaldo"
        verbose_name_plural = "Registros de Respaldos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre_original} - {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')}"
