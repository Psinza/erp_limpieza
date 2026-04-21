from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class CategoriaMateriaPrima(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías de Materias Primas"

class MateriaPrima(models.Model):
    UNIDADES = [
        ('kg', 'Kilogramos'),
        ('lt', 'Litros'),
        ('un', 'Unidades'),
    ]
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(CategoriaMateriaPrima, on_delete=models.PROTECT)
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU/Código")
    unidad_medida = models.CharField(max_length=10, choices=UNIDADES)
    stock_actual = models.DecimalField(max_digits=12, decimal_places=4, default=0.0000)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=4, default=0.0000)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

class CategoriaProductoTerminado(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías de Productos Terminados"

class ProductoTerminado(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(CategoriaProductoTerminado, on_delete=models.PROTECT)
    sku = models.CharField(max_length=50, unique=True)
    stock_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    costo_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    activo = models.BooleanField(default=True)

class Formula(models.Model):
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('activa', 'Activa'),
        ('obsoleta', 'Obsoleta'),
    ]
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    producto = models.ForeignKey(ProductoTerminado, on_delete=models.PROTECT)
    version = models.CharField(max_length=20, default='1.0')
    rendimiento = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cantidad producida por lote")
    unidad_rendimiento = models.CharField(max_length=20, default='unidades')
    instrucciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='borrador')

    def __str__(self):
        return f"{self.codigo} - {self.nombre} v{self.version}"

    @property
    def esta_activa(self):
        return self.estado == 'activa'

class LineaFormula(models.Model):
    formula = models.ForeignKey(Formula, on_delete=models.CASCADE, related_name='ingredientes')
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=12, decimal_places=4)

    def __str__(self):
        return f"{self.materia_prima.nombre} en {self.formula.nombre}"

class OrdenProduccion(models.Model):
    ESTADOS = [
        ('planificada', 'Planificada'),
        ('en_proceso', 'En Proceso'),
        ('pausada', 'Pausada'),
        ('completada', 'Completada'),
        ('anulada', 'Anulada'),
    ]
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    formula = models.ForeignKey(Formula, on_delete=models.PROTECT)
    cantidad_a_producir = models.PositiveIntegerField(default=1, help_text="Número de veces la fórmula")
    cantidad_planificada = models.PositiveIntegerField(default=0) # Alias para compatibilidad con forms
    estado = models.CharField(max_length=20, choices=ESTADOS, default='planificada')
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='media')
    fecha_planificada = models.DateField(null=True, blank=True)
    responsable = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    costo_total_real = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"OP-{self.id} | {self.formula.producto.nombre}"

class LoteProduccion(models.Model):
    ESTADOS = [
        ('en_produccion', 'En Producción'),
        ('en_control_qc', 'En Control QC'),
        ('aprobado', 'Aprobado'),
        ('liberado', 'Liberado al Almacén'),
        ('rechazado', 'Rechazado'),
    ]
    orden = models.ForeignKey(OrdenProduccion, on_delete=models.CASCADE, related_name='lotes')
    numero_lote = models.CharField(max_length=50, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='en_produccion')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    cantidad_producida = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Lote: {self.numero_lote}"

class ConsumoMateriaPrima(models.Model):
    """Registro de lo que realmente se consumió en la orden."""
    orden = models.ForeignKey(OrdenProduccion, on_delete=models.CASCADE, related_name='consumos')
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.PROTECT)
    cantidad_consumida = models.DecimalField(max_digits=12, decimal_places=4)
    costo_unitario_al_momento = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Consumo OP-{self.orden.id}: {self.materia_prima.nombre}"

class ControlCalidad(models.Model):
    lote = models.OneToOneField(LoteProduccion, on_delete=models.CASCADE, related_name='control_calidad')
    fecha_inspeccion = models.DateTimeField(auto_now_add=True)
    
    # Parámetros específicos de productos de limpieza
    ph = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="pH")
    viscosidad = models.DecimalField(max_digits=10, decimal_places=2, help_text="en cP (centipoise)")
    densidad = models.DecimalField(max_digits=6, decimal_places=3, help_text="en g/cm³")
    
    # Parámetros organolépticos
    color = models.CharField(max_length=50)
    olor = models.CharField(max_length=50)
    aspecto = models.CharField(max_length=100, help_text="Ej: Líquido traslúcido, Gel, etc.")
    
    observaciones = models.TextField(blank=True)
    aprobado = models.BooleanField(default=False)
    inspector = models.CharField(max_length=100)

    def __str__(self):
        return f"QC Lote: {self.lote.numero_lote} - {'Aprobado' if self.aprobado else 'Pendiente/Rechazado'}"

    class Meta:
        verbose_name = "Control de Calidad"
        verbose_name_plural = "Controles de Calidad"