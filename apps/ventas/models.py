# apps/ventas/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal

User = get_user_model()


# ─────────────────────────────────────────────
#  CLIENTE
# ─────────────────────────────────────────────
rif_validator = RegexValidator(
    regex=r'^[VEJGP][0-9]{7,9}$',
    message="El formato debe ser una letra (V, E, J, G, P) seguida de 7 a 9 dígitos, sin guiones."
)

class CategoriaCliente(models.Model):
    nombre      = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    descuento_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"),
        help_text="Descuento por defecto para esta categoría"
    )

    class Meta:
        verbose_name        = "Categoría de Cliente"
        verbose_name_plural = "Categorías de Cliente"
        ordering            = ["nombre"]

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    TIPO_CHOICES = [
        ("persona_natural", "Persona Natural"),
        ("empresa",         "Empresa"),
    ]
    ESTADO_CHOICES = [
        ("activo",   "Activo"),
        ("inactivo", "Inactivo"),
        ("bloqueado","Bloqueado"),
    ]
    TIPO_DOCUMENTO_CHOICES = [
        ("V", "Venezolano (V)"),
        ("E", "Extranjero (E)"),
        ("J", "Jurídico (J)"),
        ("G", "Gubernamental (G)"),
        ("P", "Pasaporte (P)"),
    ]

    # Identificación
    tipo_documento  = models.CharField(
        max_length=1, choices=TIPO_DOCUMENTO_CHOICES, default="V", verbose_name="Tipo Doc."
    )
    ruc             = models.CharField(
        max_length=20, unique=True, verbose_name="RIF / Cédula",
        validators=[rif_validator],
        help_text="Ejemplo: 12345678 (Sin la letra inicial, se unirá automáticamente)"
    )
    razon_social    = models.CharField(max_length=200, verbose_name="Razón Social / Nombre")
    nombre_comercial= models.CharField(max_length=200, blank=True)
    tipo            = models.CharField(max_length=20, choices=TIPO_CHOICES, default="empresa")
    categoria       = models.ForeignKey(
        CategoriaCliente, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="clientes"
    )

    # Contacto
    telefono        = models.CharField(max_length=30, blank=True)
    telefono2       = models.CharField(max_length=30, blank=True)
    email           = models.EmailField(blank=True)
    sitio_web       = models.URLField(blank=True)
    direccion       = models.TextField(blank=True)
    ciudad          = models.CharField(max_length=100, blank=True)
    pais            = models.CharField(max_length=100, default="Venezuela")

    # Condiciones comerciales
    dias_credito    = models.PositiveIntegerField(default=0)
    limite_credito  = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00"),
        help_text="0 = sin límite"
    )
    descuento_pct   = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )

    # Vendedor asignado
    vendedor        = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="clientes_asignados"
    )

    observaciones   = models.TextField(blank=True)
    estado          = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="activo")

    # Auditoría
    creado_por      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="clientes_creados"
    )
    creado_en       = models.DateTimeField(auto_now_add=True)
    modificado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Cliente"
        verbose_name_plural = "Clientes"
        ordering            = ["razon_social"]

    def __str__(self):
        return f"{self.razon_social} [{self.identificacion_completa}]"

    @property
    def identificacion_completa(self):
        return f"{self.tipo_documento}-{self.ruc}"

    @property
    def nombre_display(self):
        return self.nombre_comercial or self.razon_social


class ContactoCliente(models.Model):
    cliente   = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="contactos"
    )
    nombre    = models.CharField(max_length=150)
    cargo     = models.CharField(max_length=100, blank=True)
    telefono  = models.CharField(max_length=30, blank=True)
    email     = models.EmailField(blank=True)
    principal = models.BooleanField(default=False)

    class Meta:
        verbose_name        = "Contacto de Cliente"
        verbose_name_plural = "Contactos de Cliente"

    def __str__(self):
        return f"{self.nombre} ({self.cliente})"


# ─────────────────────────────────────────────
#  PRODUCTO DE VENTA
# ─────────────────────────────────────────────
class CategoriaProductoVenta(models.Model):
    nombre      = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name        = "Categoría de Producto"
        verbose_name_plural = "Categorías de Producto"
        ordering            = ["nombre"]

    def __str__(self):
        return self.nombre


class ProductoVenta(models.Model):
    UNIDAD_CHOICES = [
        ("unidad",  "Unidad"),
        ("kg",      "Kilogramo"),
        ("litro",   "Litro"),
        ("caja",    "Caja"),
        ("paquete", "Paquete"),
        ("docena",  "Docena"),
        ("metro",   "Metro"),
    ]

    codigo          = models.CharField(max_length=50, unique=True)
    nombre          = models.CharField(max_length=200)
    descripcion     = models.TextField(blank=True)
    categoria       = models.ForeignKey(
        CategoriaProductoVenta, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="productos"
    )
    unidad_medida   = models.CharField(max_length=20, choices=UNIDAD_CHOICES, default="unidad")
    precio_venta    = models.DecimalField(
        max_digits=12, decimal_places=4,
        validators=[MinValueValidator(Decimal("0.0001"))]
    )
    precio_minimo   = models.DecimalField(
        max_digits=12, decimal_places=4, default=Decimal("0.0000"),
        help_text="Precio mínimo permitido con descuento"
    )
    impuesto_pct    = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("12.00"),
        verbose_name="IVA %"
    )
    activo          = models.BooleanField(default=True)
    creado_en       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Producto de Venta"
        verbose_name_plural = "Productos de Venta"
        ordering            = ["nombre"]

    def __str__(self):
        return f"[{self.codigo}] {self.nombre}"


# ─────────────────────────────────────────────
#  COTIZACIÓN
# ─────────────────────────────────────────────
class Cotizacion(models.Model):
    ESTADO_CHOICES = [
        ("borrador",  "Borrador"),
        ("enviada",   "Enviada"),
        ("aceptada",  "Aceptada"),
        ("rechazada", "Rechazada"),
        ("vencida",   "Vencida"),
        ("convertida","Convertida a Pedido"),
    ]

    numero          = models.CharField(max_length=20, unique=True)
    cliente         = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name="cotizaciones"
    )
    fecha_emision   = models.DateField()
    fecha_vencimiento = models.DateField()
    estado          = models.CharField(max_length=12, choices=ESTADO_CHOICES, default="borrador")

    # Condiciones
    descuento_pct   = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    impuesto_pct    = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("12.00"))

    # Totales
    subtotal        = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    descuento_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    base_imponible  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    impuesto_total  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total           = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    notas           = models.TextField(blank=True)
    terminos        = models.TextField(blank=True)

    # Auditoría
    creado_por      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="cotizaciones_creadas"
    )
    creado_en       = models.DateTimeField(auto_now_add=True)
    modificado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering            = ["-fecha_emision", "-numero"]

    def __str__(self):
        return f"COT-{self.numero} | {self.cliente.nombre_display}"

    def calcular_totales(self):
        detalles            = self.detalles.all()
        self.subtotal       = sum(d.subtotal        for d in detalles)
        self.descuento_total= sum(d.descuento_monto for d in detalles)
        self.base_imponible = self.subtotal - self.descuento_total
        self.impuesto_total = self.base_imponible * (self.impuesto_pct / Decimal("100"))
        self.total          = self.base_imponible + self.impuesto_total
        self.save()

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


class DetalleCotizacion(models.Model):
    cotizacion      = models.ForeignKey(
        Cotizacion, on_delete=models.CASCADE, related_name="detalles"
    )
    producto        = models.ForeignKey(
        ProductoVenta, on_delete=models.PROTECT, related_name="detalles_cotizacion"
    )
    descripcion     = models.CharField(max_length=300, blank=True)
    cantidad        = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    precio_unitario = models.DecimalField(
        max_digits=12, decimal_places=4,
        validators=[MinValueValidator(Decimal("0.0001"))]
    )
    descuento_pct   = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    descuento_monto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal        = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name        = "Detalle de Cotización"
        verbose_name_plural = "Detalles de Cotización"

    def __str__(self):
        return f"{self.cotizacion} | {self.producto}"

    def save(self, *args, **kwargs):
        self.descuento_monto = (
            self.cantidad * self.precio_unitario * (self.descuento_pct / Decimal("100"))
        )
        self.subtotal = (self.cantidad * self.precio_unitario) - self.descuento_monto
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────
#  PEDIDO (ORDEN DE VENTA)
# ─────────────────────────────────────────────
class Pedido(models.Model):
    ESTADO_CHOICES = [
        ("borrador",    "Borrador"),
        ("confirmado",  "Confirmado"),
        ("en_proceso",  "En Proceso"),
        ("despachado",  "Despachado"),
        ("entregado",   "Entregado"),
        ("facturado",   "Facturado"),
        ("anulado",     "Anulado"),
    ]

    numero          = models.CharField(max_length=20, unique=True)
    cliente         = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name="pedidos"
    )
    cotizacion      = models.OneToOneField(
        Cotizacion, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="pedido"
    )
    fecha_pedido    = models.DateField()
    fecha_entrega   = models.DateField(null=True, blank=True)
    estado          = models.CharField(max_length=15, choices=ESTADO_CHOICES, default="borrador")

    # Dirección de entrega
    direccion_entrega = models.TextField(blank=True)

    # Condiciones
    dias_credito    = models.PositiveIntegerField(default=0)
    descuento_pct   = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    impuesto_pct    = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("12.00"))

    # Totales
    subtotal        = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    descuento_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    base_imponible  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    impuesto_total  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total           = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    notas           = models.TextField(blank=True)

    # Auditoría
    creado_por      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="pedidos_creados"
    )
    aprobado_por    = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pedidos_aprobados"
    )
    creado_en       = models.DateTimeField(auto_now_add=True)
    modificado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering            = ["-fecha_pedido", "-numero"]

    def __str__(self):
        return f"PED-{self.numero} | {self.cliente.nombre_display}"

    def calcular_totales(self):
        detalles            = self.detalles.all()
        self.subtotal       = sum(d.subtotal        for d in detalles)
        self.descuento_total= sum(d.descuento_monto for d in detalles)
        self.base_imponible = self.subtotal - self.descuento_total
        self.impuesto_total = self.base_imponible * (self.impuesto_pct / Decimal("100"))
        self.total          = self.base_imponible + self.impuesto_total
        self.save()

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


class DetallePedido(models.Model):
    pedido          = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name="detalles"
    )
    producto        = models.ForeignKey(
        ProductoVenta, on_delete=models.PROTECT, related_name="detalles_pedido"
    )
    descripcion     = models.CharField(max_length=300, blank=True)
    cantidad        = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    precio_unitario = models.DecimalField(
        max_digits=12, decimal_places=4,
        validators=[MinValueValidator(Decimal("0.0001"))]
    )
    descuento_pct   = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    descuento_monto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal        = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    cantidad_despachada = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    class Meta:
        verbose_name        = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedido"

    def __str__(self):
        return f"{self.pedido} | {self.producto}"

    def save(self, *args, **kwargs):
        self.descuento_monto = (
            self.cantidad * self.precio_unitario * (self.descuento_pct / Decimal("100"))
        )
        self.subtotal = (self.cantidad * self.precio_unitario) - self.descuento_monto
        super().save(*args, **kwargs)

    @property
    def pendiente_despachar(self):
        return self.cantidad - self.cantidad_despachada


# ─────────────────────────────────────────────
#  DESPACHO
# ─────────────────────────────────────────────
class Despacho(models.Model):
    ESTADO_CHOICES = [
        ("preparando", "Preparando"),
        ("despachado", "Despachado"),
        ("entregado",  "Entregado"),
    ]

    pedido          = models.ForeignKey(
        Pedido, on_delete=models.PROTECT, related_name="despachos"
    )
    numero          = models.CharField(max_length=20, unique=True)
    fecha_despacho  = models.DateField()
    transportista   = models.CharField(max_length=200, blank=True)
    numero_guia     = models.CharField(max_length=100, blank=True)
    estado          = models.CharField(max_length=12, choices=ESTADO_CHOICES, default="preparando")
    observaciones   = models.TextField(blank=True)
    despachado_por  = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="despachos_realizados"
    )
    creado_en       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Despacho"
        verbose_name_plural = "Despachos"
        ordering            = ["-fecha_despacho"]

    def __str__(self):
        return f"DESP-{self.numero} | {self.pedido}"

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


class DetalleDespacho(models.Model):
    despacho        = models.ForeignKey(
        Despacho, on_delete=models.CASCADE, related_name="detalles"
    )
    detalle_pedido  = models.ForeignKey(
        DetallePedido, on_delete=models.PROTECT, related_name="despachos"
    )
    cantidad_despachada = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    observacion     = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name        = "Detalle de Despacho"
        verbose_name_plural = "Detalles de Despacho"

    def __str__(self):
        return f"{self.despacho} | {self.detalle_pedido.producto}"
