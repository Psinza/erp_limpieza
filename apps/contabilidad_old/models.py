from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal

class EjercicioContable(models.Model):
    """Representa un año fiscal o periodo contable anual."""
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Ejercicio")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Finalización")
    abierto = models.BooleanField(default=True, verbose_name="¿Está Abierto?")

    class Meta:
        verbose_name = "Ejercicio Contable"
        verbose_name_plural = "Ejercicios Contables"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.nombre} ({'Abierto' if self.abierto else 'Cerrado'})"

class CuentaContable(models.Model):
    """Plan de Cuentas jerárquico."""
    NATURALEZA_CHOICES = [
        ('deudora', 'Deudora (Activos, Costos, Gastos)'),
        ('acreedora', 'Acreedora (Pasivos, Patrimonio, Ingresos)')
    ]
    TIPO_CHOICES = [
        ('activo', 'Activo'), ('pasivo', 'Pasivo'), ('patrimonio', 'Patrimonio'),
        ('ingreso', 'Ingreso'), ('costo', 'Costo'), ('egreso', 'Gasto')
    ]
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código/Cuenta")
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Cuenta")
    padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='hijos', verbose_name="Cuenta Padre")
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, verbose_name="Tipo de Cuenta")
    naturaleza = models.CharField(max_length=10, choices=NATURALEZA_CHOICES, verbose_name="Naturaleza")
    saldo_actual = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'), verbose_name="Saldo Actual")

    class Meta:
        verbose_name = "Cuenta Contable"
        verbose_name_plural = "Plan de Cuentas"
        ordering = ['codigo']

    def __str__(self): return f"{self.codigo} - {self.nombre}"

class AsientoContable(models.Model):
    """Encabezado de un comprobante de diario."""
    ESTADO_CHOICES = [('borrador', 'Borrador'), ('aprobado', 'Aprobado'), ('anulado', 'Anulado')]
    ejercicio = models.ForeignKey(EjercicioContable, on_delete=models.PROTECT, verbose_name="Ejercicio")
    fecha = models.DateField(verbose_name="Fecha Contable")
    glosa = models.TextField(verbose_name="Descripción/Concepto")
    numero = models.CharField(max_length=20, unique=True, verbose_name="Número de Comprobante")
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='borrador', verbose_name="Estado")
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Usuario")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Asiento Contable"
        verbose_name_plural = "Asientos Contables"

    def __str__(self): return f"Asiento {self.numero} ({self.fecha})"

    @property
    def total_debe(self):
        return self.lineas.aggregate(total=models.Sum('debe'))['total'] or Decimal('0.00')

    @property
    def total_haber(self):
        return self.lineas.aggregate(total=models.Sum('haber'))['total'] or Decimal('0.00')

    def balanceado(self):
        """Verifica si el debe es igual al haber y si hay líneas."""
        debe = self.total_debe
        haber = self.total_haber
        return debe == haber and debe > 0

class LineaAsiento(models.Model):
    """Detalle de movimiento (Debe/Haber) de un asiento."""
    asiento = models.ForeignKey(AsientoContable, related_name='lineas', on_delete=models.CASCADE, verbose_name="Asiento")
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT, verbose_name="Cuenta")
    debe = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Debe")
    haber = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Haber")
    referencia = models.CharField(max_length=100, blank=True, verbose_name="Referencia Externa")

    class Meta:
        verbose_name = "Línea de Asiento"
        verbose_name_plural = "Líneas de Asiento"

    def clean(self):
        if self.debe > 0 and self.haber > 0:
            raise ValidationError("Una sola línea no puede tener valores en el Debe y el Haber simultáneamente.")
        if self.debe == 0 and self.haber == 0:
            raise ValidationError("La línea debe tener al menos un valor en el Debe o en el Haber.")

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.asiento.estado == 'aprobado':
            # Lógica para actualizar saldos si el asiento se está aprobando
            diff = self.debe - self.haber
            if self.cuenta.naturaleza == 'acreedora':
                diff = self.haber - self.debe
            # Nota: En sistemas reales, esto se suele hacer mediante una señal o un Manager
            # para evitar duplicidad de saldos en ediciones.
            CuentaContable.objects.filter(pk=self.cuenta.pk).update(saldo_actual=models.F('saldo_actual') + diff)
        super().save(*args, **kwargs)