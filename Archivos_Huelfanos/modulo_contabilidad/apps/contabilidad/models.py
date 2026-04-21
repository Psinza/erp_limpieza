# apps/contabilidad/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


# ─────────────────────────────────────────────
#  EJERCICIO CONTABLE
# ─────────────────────────────────────────────
class EjercicioContable(models.Model):
    ESTADO_CHOICES = [
        ("abierto",  "Abierto"),
        ("cerrado",  "Cerrado"),
    ]

    nombre          = models.CharField(max_length=100, unique=True,
                                       help_text="Ej: Ejercicio 2025")
    año             = models.PositiveIntegerField()
    fecha_inicio    = models.DateField()
    fecha_fin       = models.DateField()
    estado          = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="abierto")
    creado_por      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="ejercicios_creados"
    )
    creado_en       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Ejercicio Contable"
        verbose_name_plural = "Ejercicios Contables"
        ordering            = ["-año"]

    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"


# ─────────────────────────────────────────────
#  PLAN DE CUENTAS
# ─────────────────────────────────────────────
class CuentaContable(models.Model):
    TIPO_CHOICES = [
        ("activo",      "Activo"),
        ("pasivo",      "Pasivo"),
        ("patrimonio",  "Patrimonio"),
        ("ingreso",     "Ingreso"),
        ("egreso",      "Egreso / Gasto"),
        ("costo",       "Costo de Ventas"),
    ]
    NATURALEZA_CHOICES = [
        ("deudora",    "Deudora"),
        ("acreedora",  "Acreedora"),
    ]

    codigo          = models.CharField(max_length=20, unique=True,
                                       help_text="Ej: 1.1.01, 2.1.01")
    nombre          = models.CharField(max_length=200)
    tipo            = models.CharField(max_length=12, choices=TIPO_CHOICES)
    naturaleza      = models.CharField(max_length=10, choices=NATURALEZA_CHOICES)
    padre           = models.ForeignKey(
        "self", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="hijos"
    )
    nivel           = models.PositiveIntegerField(default=1,
                                                  help_text="1=Grupo, 2=Subgrupo, 3=Cuenta, 4=Subcuenta")
    acepta_movimientos = models.BooleanField(
        default=True,
        help_text="False = cuenta de agrupación (solo suma hijos)"
    )
    saldo_inicial   = models.DecimalField(
        max_digits=16, decimal_places=2, default=Decimal("0.00")
    )
    saldo_actual    = models.DecimalField(
        max_digits=16, decimal_places=2, default=Decimal("0.00")
    )
    activa          = models.BooleanField(default=True)
    descripcion     = models.TextField(blank=True)

    class Meta:
        verbose_name        = "Cuenta Contable"
        verbose_name_plural = "Plan de Cuentas"
        ordering            = ["codigo"]

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"

    @property
    def saldo_debe(self):
        from django.db.models import Sum
        return self.lineas.filter(tipo="debe").aggregate(
            t=Sum("monto")
        )["t"] or Decimal("0.00")

    @property
    def saldo_haber(self):
        from django.db.models import Sum
        return self.lineas.filter(tipo="haber").aggregate(
            t=Sum("monto")
        )["t"] or Decimal("0.00")

    def recalcular_saldo(self):
        if self.naturaleza == "deudora":
            self.saldo_actual = self.saldo_inicial + self.saldo_debe - self.saldo_haber
        else:
            self.saldo_actual = self.saldo_inicial + self.saldo_haber - self.saldo_debe
        self.save(update_fields=["saldo_actual"])


# ─────────────────────────────────────────────
#  ASIENTO CONTABLE
# ─────────────────────────────────────────────
class AsientoContable(models.Model):
    TIPO_CHOICES = [
        ("diario",      "Asiento de Diario"),
        ("apertura",    "Asiento de Apertura"),
        ("ajuste",      "Asiento de Ajuste"),
        ("cierre",      "Asiento de Cierre"),
        ("reclasif",    "Reclasificación"),
    ]
    ESTADO_CHOICES = [
        ("borrador",  "Borrador"),
        ("aprobado",  "Aprobado"),
        ("anulado",   "Anulado"),
    ]

    numero          = models.CharField(max_length=20, unique=True)
    ejercicio       = models.ForeignKey(
        EjercicioContable, on_delete=models.PROTECT, related_name="asientos"
    )
    fecha           = models.DateField()
    tipo            = models.CharField(max_length=10, choices=TIPO_CHOICES, default="diario")
    concepto        = models.CharField(max_length=400)
    referencia      = models.CharField(max_length=100, blank=True)
    estado          = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="borrador")

    total_debe      = models.DecimalField(
        max_digits=16, decimal_places=2, default=Decimal("0.00")
    )
    total_haber     = models.DecimalField(
        max_digits=16, decimal_places=2, default=Decimal("0.00")
    )

    creado_por      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="asientos_creados"
    )
    aprobado_por    = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="asientos_aprobados"
    )
    creado_en       = models.DateTimeField(auto_now_add=True)
    modificado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Asiento Contable"
        verbose_name_plural = "Asientos Contables"
        ordering            = ["-fecha", "-numero"]

    def __str__(self):
        return f"AST-{self.numero} | {self.fecha} | {self.concepto[:50]}"

    @property
    def esta_cuadrado(self):
        return self.total_debe == self.total_haber

    def calcular_totales(self):
        from django.db.models import Sum
        self.total_debe  = self.lineas.filter(tipo="debe").aggregate(
            t=Sum("monto"))["t"] or Decimal("0.00")
        self.total_haber = self.lineas.filter(tipo="haber").aggregate(
            t=Sum("monto"))["t"] or Decimal("0.00")
        self.save(update_fields=["total_debe", "total_haber"])

    def aprobar(self, user):
        if not self.esta_cuadrado:
            raise ValueError("El asiento no está cuadrado (Debe ≠ Haber)")
        self.estado       = "aprobado"
        self.aprobado_por = user
        self.save()
        # Actualizar saldos de cuentas
        for linea in self.lineas.select_related("cuenta"):
            linea.cuenta.recalcular_saldo()

    def anular(self):
        if self.estado == "aprobado":
            # Revertir saldos
            for linea in self.lineas.select_related("cuenta"):
                linea.cuenta.recalcular_saldo()
        self.estado = "anulado"
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
        return f"{year}-{seq:05d}"


class LineaAsiento(models.Model):
    TIPO_CHOICES = [
        ("debe",  "Debe"),
        ("haber", "Haber"),
    ]

    asiento         = models.ForeignKey(
        AsientoContable, on_delete=models.CASCADE, related_name="lineas"
    )
    cuenta          = models.ForeignKey(
        CuentaContable, on_delete=models.PROTECT, related_name="lineas"
    )
    tipo            = models.CharField(max_length=5, choices=TIPO_CHOICES)
    monto           = models.DecimalField(
        max_digits=16, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    descripcion     = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name        = "Línea de Asiento"
        verbose_name_plural = "Líneas de Asiento"
        ordering            = ["tipo", "cuenta__codigo"]

    def __str__(self):
        return f"{self.asiento} | {self.cuenta} | {self.get_tipo_display()} ${self.monto}"


# ─────────────────────────────────────────────
#  PERÍODO CONTABLE (mes)
# ─────────────────────────────────────────────
class PeriodoContable(models.Model):
    ESTADO_CHOICES = [
        ("abierto", "Abierto"),
        ("cerrado", "Cerrado"),
    ]

    ejercicio       = models.ForeignKey(
        EjercicioContable, on_delete=models.CASCADE, related_name="periodos"
    )
    mes             = models.PositiveIntegerField()
    nombre          = models.CharField(max_length=50)
    fecha_inicio    = models.DateField()
    fecha_fin       = models.DateField()
    estado          = models.CharField(max_length=8, choices=ESTADO_CHOICES, default="abierto")

    class Meta:
        verbose_name        = "Período Contable"
        verbose_name_plural = "Períodos Contables"
        ordering            = ["ejercicio", "mes"]
        unique_together     = ["ejercicio", "mes"]

    def __str__(self):
        return f"{self.nombre} — {self.ejercicio}"


# ─────────────────────────────────────────────
#  CONFIGURACIÓN CONTABLE
# ─────────────────────────────────────────────
class ConfiguracionContable(models.Model):
    """Mapeo de cuentas para generación automática de asientos."""
    clave           = models.CharField(max_length=100, unique=True,
                                       help_text="Ej: CAJA_GENERAL, VENTAS, COSTO_VENTA")
    descripcion     = models.CharField(max_length=200)
    cuenta          = models.ForeignKey(
        CuentaContable, on_delete=models.PROTECT, related_name="configuraciones"
    )

    class Meta:
        verbose_name        = "Configuración Contable"
        verbose_name_plural = "Configuraciones Contables"

    def __str__(self):
        return f"{self.clave} → {self.cuenta}"
