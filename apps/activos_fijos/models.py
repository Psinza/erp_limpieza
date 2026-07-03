from django.db import models
from datetime import date

class CategoriaActivo(models.Model):
    nombre = models.CharField(max_length=100)
    prefijo_codigo = models.CharField(max_length=5, help_text="Ej: MAQ para Maquinaria")
    vida_util_defecto = models.PositiveIntegerField(default=5)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Categorías de Activos"

class ActivoFijo(models.Model):
    METODOS_DEPRECIACION = [
        ('lineal', 'Líneal'),
        ('decremento', 'Decremento Doble'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código de Inventario (Bien Nacional)")
    etiqueta = models.CharField(max_length=100, blank=True, null=True, verbose_name="Etiqueta / Código de Barras", help_text="Para control físico")
    serial = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Serial")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Activo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción detallada (Sudebip)")
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    anio_fabricacion = models.PositiveIntegerField(blank=True, null=True, verbose_name="Año de Fabricación")
    categoria = models.ForeignKey(CategoriaActivo, on_delete=models.PROTECT, related_name='activos', null=True, blank=True, verbose_name="Clasificación / Tipo de Activo")
    fecha_adquisicion = models.DateField(verbose_name="Fecha de Adquisición / Incorporación")
    valor_compra = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Costo / Valor de Adquisición")
    valor_residual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vida_util_anios = models.PositiveIntegerField(default=5, verbose_name="Años de Vida Útil")
    metodo_depreciacion = models.CharField(max_length=20, choices=METODOS_DEPRECIACION, default='lineal')
    estado = models.CharField(max_length=50, default='Operativo', verbose_name="Estado de Conservación")
    ubicacion = models.CharField(max_length=200, blank=True, verbose_name="Ubicación Física")
    responsable = models.ForeignKey('rrhh.Empleado', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Responsable Directo")

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

class AsignacionActivo(models.Model):
    activo = models.ForeignKey(ActivoFijo, on_delete=models.CASCADE, related_name='asignaciones')
    empleado = models.CharField(max_length=200, help_text="Nombre del empleado o responsable")
    departamento = models.CharField(max_length=100)
    fecha_asignacion = models.DateField()
    fecha_devolucion = models.DateField(null=True, blank=True)
    estado_entrega = models.CharField(max_length=100, default='Buen estado')
    estado_devolucion = models.CharField(max_length=100, null=True, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.activo.codigo} asignado a {self.empleado}"
        
class MantenimientoActivo(models.Model):
    TIPOS_MANTENIMIENTO = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
    ]
    
    activo = models.ForeignKey(ActivoFijo, on_delete=models.CASCADE, related_name='mantenimientos')
    fecha_mantenimiento = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPOS_MANTENIMIENTO)
    descripcion = models.TextField()
    proveedor = models.CharField(max_length=200)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    proximo_mantenimiento = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Mantenimiento {self.tipo} - {self.activo.codigo} ({self.fecha_mantenimiento})"