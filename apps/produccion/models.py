from django.conf import settings
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
        ('gr', 'Gramos'),
        ('ml', 'Mililitros'),
    ]
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(CategoriaMateriaPrima, on_delete=models.PROTECT, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="SKU/Código")
    concentracion = models.DecimalField(max_digits=5, decimal_places=2, default=100.00, help_text="Pureza o Concentración %")
    unidad_medida = models.CharField(max_length=10, choices=UNIDADES)
    stock_actual = models.DecimalField(max_digits=12, decimal_places=4, default=0.0000)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=4, default=0.0000)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.concentracion}%)"

class CategoriaProductoTerminado(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías de Productos Terminados"

class ProductoTerminado(models.Model):
    PRESENTACIONES = [
        ('1L', 'Envase 1 Litro'),
        ('3.78L', 'Galón 3.78 Litros'),
        ('5L', 'Envase 5 Litros'),
        ('10L', 'Envase 10 Litros'),
        ('20L', 'Bidón 20 Litros'),
        ('200L', 'Tambor 200 Litros'),
    ]
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(CategoriaProductoTerminado, on_delete=models.PROTECT)
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    presentacion = models.CharField(max_length=10, choices=PRESENTACIONES, default='1L')
    registro_sanitario = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nro Registro Sanitario / CPE")
    normativa_covenin = models.CharField(max_length=100, blank=True, null=True, help_text="Norma COVENIN aplicable")
    stock_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    costo_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.get_presentacion_display()}"

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
    procedimiento = models.TextField(blank=True, help_text="Pasos detallados de mezclado y seguridad (EPI)")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='borrador')

    def __str__(self):
        return f"{self.codigo} - {self.nombre} v{self.version}"

class LineaFormula(models.Model):
    formula = models.ForeignKey(Formula, on_delete=models.CASCADE, related_name='ingredientes')
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=12, decimal_places=4)
    es_empaque = models.BooleanField(default=False, help_text="Marcar si es envase, tapa o etiqueta")

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
    lote_numero = models.CharField(max_length=50, unique=True, null=True, verbose_name="Nro de Lote Asignado")
    cantidad_a_producir = models.PositiveIntegerField(default=1, help_text="Número de veces la fórmula")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='planificada')
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='media')
    fecha_planificada = models.DateField(null=True, blank=True)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    costo_total_real = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"OP-{self.id} | {self.lote_numero} | {self.formula.producto.nombre}"

class ControlCalidad(models.Model):
    orden = models.OneToOneField(OrdenProduccion, on_delete=models.CASCADE, related_name='control_calidad', null=True, blank=True)
    fecha_inspeccion = models.DateTimeField(auto_now_add=True)
    
    # Parámetros Químicos
    ph = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="pH", null=True, blank=True)
    viscosidad = models.DecimalField(max_digits=10, decimal_places=2, help_text="en cP (centipoise)", null=True, blank=True)
    densidad = models.DecimalField(max_digits=6, decimal_places=3, help_text="en g/cm³", null=True, blank=True)
    concentracion_activo = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="% Ingrediente Activo", null=True, blank=True)
    
    # Parámetros organolépticos
    color = models.CharField(max_length=50, blank=True)
    olor = models.CharField(max_length=50, blank=True)
    aspecto = models.CharField(max_length=100, help_text="Ej: Líquido traslúcido, Gel, etc.", blank=True)
    
    # Cumplimiento
    cumple_covenin = models.BooleanField(default=False, verbose_name="Cumple Normas COVENIN")
    estabilidad_alcalina = models.BooleanField(default=True, verbose_name="Estabilidad Química")
    
    observaciones = models.TextField(blank=True)
    aprobado = models.BooleanField(default=False)
    inspector = models.CharField(max_length=100)

    def __str__(self):
        return f"QC Lote: {self.orden.lote_numero} - {'APROBADO' if self.aprobado else 'FALLIDO/PENDIENTE'}"


    class Meta:
        verbose_name = "Control de Calidad"
        verbose_name_plural = "Controles de Calidad"
