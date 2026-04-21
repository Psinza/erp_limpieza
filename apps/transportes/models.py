# apps/transportes/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


# ─────────────────────────────────────────────
#  VEHÍCULOS
# ─────────────────────────────────────────────
class TipoVehiculo(models.Model):
    nombre      = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name        = "Tipo de Vehículo"
        verbose_name_plural = "Tipos de Vehículo"
        ordering            = ["nombre"]

    def __str__(self):
        return self.nombre


class Vehiculo(models.Model):
    ESTADO_CHOICES = [
        ("disponible",  "Disponible"),
        ("en_ruta",     "En Ruta"),
        ("mantenimiento","En Mantenimiento"),
        ("inactivo",    "Inactivo"),
    ]
    COMBUSTIBLE_CHOICES = [
        ("gasolina", "Gasolina"),
        ("diesel",   "Diésel"),
        ("gas",      "Gas"),
        ("electrico","Eléctrico"),
        ("hibrido",  "Híbrido"),
    ]

    placa           = models.CharField(max_length=20, unique=True)
    tipo            = models.ForeignKey(
        TipoVehiculo, on_delete=models.PROTECT, related_name="vehiculos"
    )
    marca           = models.CharField(max_length=100)
    modelo          = models.CharField(max_length=100)
    año             = models.PositiveIntegerField()
    color           = models.CharField(max_length=50, blank=True)
    combustible     = models.CharField(
        max_length=10, choices=COMBUSTIBLE_CHOICES, default="gasolina"
    )
    capacidad_carga = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00"),
        help_text="Capacidad en toneladas"
    )
    capacidad_volumen = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00"),
        help_text="Capacidad en m³"
    )
    odometro        = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Odómetro (km)"
    )
    estado          = models.CharField(
        max_length=15, choices=ESTADO_CHOICES, default="disponible"
    )

    # Documentos
    soat_vencimiento       = models.DateField(null=True, blank=True, verbose_name="Vencimiento SOAT")
    revision_vencimiento   = models.DateField(null=True, blank=True, verbose_name="Vencimiento Revisión Técnica")
    seguro_vencimiento     = models.DateField(null=True, blank=True, verbose_name="Vencimiento Seguro")

    foto            = models.FileField(upload_to="vehiculos/", blank=True, null=True)
    observaciones   = models.TextField(blank=True)
    creado_en       = models.DateTimeField(auto_now_add=True)
    modificado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering            = ["placa"]

    def __str__(self):
        return f"{self.placa} — {self.marca} {self.modelo} ({self.año})"

    @property
    def documentos_vencidos(self):
        from django.utils import timezone
        hoy = timezone.now().date()
        vencidos = []
        if self.soat_vencimiento and self.soat_vencimiento < hoy:
            vencidos.append("SOAT")
        if self.revision_vencimiento and self.revision_vencimiento < hoy:
            vencidos.append("Revisión Técnica")
        if self.seguro_vencimiento and self.seguro_vencimiento < hoy:
            vencidos.append("Seguro")
        return vencidos


# ─────────────────────────────────────────────
#  CONDUCTORES
# ─────────────────────────────────────────────
class Conductor(models.Model):
    ESTADO_CHOICES = [
        ("activo",     "Activo"),
        ("inactivo",   "Inactivo"),
        ("suspendido", "Suspendido"),
        ("vacaciones", "De Vacaciones"),
    ]
    CATEGORIA_LICENCIA_CHOICES = [
        ("A",   "A — Motos"),
        ("B",   "B — Vehículo liviano"),
        ("C",   "C — Camión"),
        ("D",   "D — Bus"),
        ("E",   "E — Articulado"),
        ("F",   "F — Maquinaria pesada"),
    ]

    cedula              = models.CharField(max_length=20, unique=True)
    nombres             = models.CharField(max_length=100)
    apellidos           = models.CharField(max_length=100)
    telefono            = models.CharField(max_length=20, blank=True)
    email               = models.EmailField(blank=True)
    direccion           = models.TextField(blank=True)

    # Licencia
    numero_licencia     = models.CharField(max_length=30, blank=True)
    categoria_licencia  = models.CharField(
        max_length=2, choices=CATEGORIA_LICENCIA_CHOICES, blank=True
    )
    licencia_vencimiento= models.DateField(null=True, blank=True)

    estado              = models.CharField(
        max_length=12, choices=ESTADO_CHOICES, default="activo"
    )
    foto                = models.FileField(
        upload_to="conductores/", blank=True, null=True
    )
    vehiculo_asignado   = models.ForeignKey(
        Vehiculo, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="conductores"
    )
    observaciones       = models.TextField(blank=True)
    creado_en           = models.DateTimeField(auto_now_add=True)
    modificado_en       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Conductor"
        verbose_name_plural = "Conductores"
        ordering            = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.apellidos}, {self.nombres} [{self.cedula}]"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def licencia_vencida(self):
        from django.utils import timezone
        if self.licencia_vencimiento:
            return self.licencia_vencimiento < timezone.now().date()
        return False


# ─────────────────────────────────────────────
#  ZONAS Y RUTAS
# ─────────────────────────────────────────────
class Zona(models.Model):
    nombre      = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activa      = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Zona"
        verbose_name_plural = "Zonas"
        ordering            = ["nombre"]

    def __str__(self):
        return self.nombre


class Ruta(models.Model):
    ESTADO_CHOICES = [
        ("activa",   "Activa"),
        ("inactiva", "Inactiva"),
    ]

    codigo          = models.CharField(max_length=20, unique=True)
    nombre          = models.CharField(max_length=200)
    zona            = models.ForeignKey(
        Zona, on_delete=models.PROTECT, related_name="rutas"
    )
    origen          = models.CharField(max_length=200)
    destino         = models.CharField(max_length=200)
    distancia_km    = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00")
    )
    tiempo_estimado = models.PositiveIntegerField(
        default=0, help_text="Tiempo estimado en minutos"
    )
    descripcion     = models.TextField(blank=True)
    estado          = models.CharField(
        max_length=10, choices=ESTADO_CHOICES, default="activa"
    )
    creado_en       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Ruta"
        verbose_name_plural = "Rutas"
        ordering            = ["zona", "codigo"]

    def __str__(self):
        return f"{self.codigo} — {self.nombre} ({self.origen} → {self.destino})"


class PuntoEntrega(models.Model):
    """Parada específica dentro de una ruta."""
    ruta            = models.ForeignKey(
        Ruta, on_delete=models.CASCADE, related_name="puntos"
    )
    orden           = models.PositiveIntegerField()
    nombre          = models.CharField(max_length=200)
    direccion       = models.TextField(blank=True)
    cliente_ref     = models.CharField(max_length=200, blank=True,
                                       help_text="Nombre del cliente en este punto")
    tiempo_estimado = models.PositiveIntegerField(
        default=0, help_text="Minutos desde el inicio de la ruta"
    )
    activo          = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Punto de Entrega"
        verbose_name_plural = "Puntos de Entrega"
        ordering            = ["ruta", "orden"]
        unique_together     = ["ruta", "orden"]

    def __str__(self):
        return f"{self.ruta.codigo} | #{self.orden} — {self.nombre}"


# ─────────────────────────────────────────────
#  DESPACHO / VIAJE
# ─────────────────────────────────────────────
class Despacho(models.Model):
    ESTADO_CHOICES = [
        ("programado",  "Programado"),
        ("en_ruta",     "En Ruta"),
        ("completado",  "Completado"),
        ("cancelado",   "Cancelado"),
        ("con_novedad", "Con Novedad"),
    ]

    numero          = models.CharField(max_length=20, unique=True)
    ruta            = models.ForeignKey(
        Ruta, on_delete=models.PROTECT, related_name="despachos"
    )
    vehiculo        = models.ForeignKey(
        Vehiculo, on_delete=models.PROTECT, related_name="despachos"
    )
    conductor       = models.ForeignKey(
        Conductor, on_delete=models.PROTECT, related_name="despachos"
    )

    fecha_salida    = models.DateTimeField()
    fecha_llegada_estimada = models.DateTimeField(null=True, blank=True)
    fecha_llegada_real     = models.DateTimeField(null=True, blank=True)

    estado          = models.CharField(
        max_length=15, choices=ESTADO_CHOICES, default="programado"
    )

    # Métricas
    odometro_salida  = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    odometro_llegada = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    km_recorridos    = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    combustible_usado= models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00"),
        help_text="Galones/litros usados"
    )
    costo_combustible= models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    notas           = models.TextField(blank=True)
    novedad         = models.TextField(blank=True, help_text="Descripción de novedad si aplica")

    # Auditoría
    creado_por      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="despachos_creados"
    )
    creado_en       = models.DateTimeField(auto_now_add=True)
    modificado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Despacho"
        verbose_name_plural = "Despachos"
        ordering            = ["-fecha_salida"]

    def __str__(self):
        return f"DSP-{self.numero} | {self.ruta.codigo} | {self.vehiculo.placa}"

    @classmethod
    def generar_numero(cls):
        from django.utils import timezone
        year  = timezone.now().year
        ultimo = cls.objects.filter(numero__startswith=str(year)).order_by("-numero").first()
        seq = 1
        if ultimo:
            try:
                seq = int(ultimo.numero.split("-")[-1]) + 1
            except (ValueError, IndexError):
                pass
        return f"{year}-{seq:04d}"


class EntregaDespacho(models.Model):
    """Registro de entrega en cada punto durante el despacho."""
    ESTADO_CHOICES = [
        ("pendiente",  "Pendiente"),
        ("entregado",  "Entregado"),
        ("no_entregado","No Entregado"),
        ("parcial",    "Entrega Parcial"),
    ]

    despacho        = models.ForeignKey(
        Despacho, on_delete=models.CASCADE, related_name="entregas"
    )
    punto_entrega   = models.ForeignKey(
        PuntoEntrega, on_delete=models.PROTECT, related_name="entregas"
    )
    hora_llegada    = models.DateTimeField(null=True, blank=True)
    estado          = models.CharField(
        max_length=15, choices=ESTADO_CHOICES, default="pendiente"
    )
    firma_receptor  = models.CharField(max_length=200, blank=True)
    observacion     = models.TextField(blank=True)

    class Meta:
        verbose_name        = "Entrega de Despacho"
        verbose_name_plural = "Entregas de Despacho"
        ordering            = ["punto_entrega__orden"]

    def __str__(self):
        return f"{self.despacho} | {self.punto_entrega.nombre}"


# ─────────────────────────────────────────────
#  MANTENIMIENTO
# ─────────────────────────────────────────────
class Mantenimiento(models.Model):
    TIPO_CHOICES = [
        ("preventivo",  "Preventivo"),
        ("correctivo",  "Correctivo"),
        ("revision",    "Revisión"),
    ]
    ESTADO_CHOICES = [
        ("programado",  "Programado"),
        ("en_proceso",  "En Proceso"),
        ("completado",  "Completado"),
        ("cancelado",   "Cancelado"),
    ]

    vehiculo        = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="mantenimientos"
    )
    tipo            = models.CharField(max_length=12, choices=TIPO_CHOICES)
    descripcion     = models.CharField(max_length=300)
    fecha_programada= models.DateField()
    fecha_ejecucion = models.DateField(null=True, blank=True)
    estado          = models.CharField(
        max_length=12, choices=ESTADO_CHOICES, default="programado"
    )
    costo           = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    taller          = models.CharField(max_length=200, blank=True)
    km_en_servicio  = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    observaciones   = models.TextField(blank=True)
    creado_por      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="mantenimientos_creados"
    )
    creado_en       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering            = ["-fecha_programada"]

    def __str__(self):
        return f"{self.vehiculo.placa} | {self.get_tipo_display()} | {self.fecha_programada}"
