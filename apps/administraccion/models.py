from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

class Empresa(models.Model):
    nombre = models.CharField(max_length=200)
    error_log = models.TextField(null=True, blank=True)
    
    # Campos de Auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='respaldos_creados')
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='respaldos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='respaldos_modificados')
    modificado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='respaldos_modificados')
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre_original} - {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')}"
        return f"{self.nombre_original} - {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')}"