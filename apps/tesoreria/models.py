from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class Banco(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, blank=True, null=True)
    pais = models.CharField(max_length=50, default='Ecuador')
    activo = models.BooleanField(default=True)
    def __str__(self): return self.nombre

class CuentaBancaria(models.Model):
    TIPO_CHOICES = [('ahorros', 'Ahorros'), ('corriente', 'Corriente')]
    banco = models.ForeignKey(Banco, on_delete=models.CASCADE)
    numero = models.CharField(max_length=50, unique=True)
    alias = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    moneda = models.CharField(max_length=10, default='USD')
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    titular = models.CharField(max_length=200, blank=True, null=True)
    activa = models.BooleanField(default=True)
    def __str__(self): return f"{self.banco} - {self.numero}"

class MovimientoBancario(models.Model):
    TIPO_M_CHOICES = [('ingreso', 'Ingreso / Crédito'), ('egreso', 'Egreso / Débito')]
    cuenta = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE, related_name="movimientos")
    fecha = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPO_M_CHOICES)
    concepto = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField()
    referencia = models.CharField(max_length=100, blank=True, null=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.tipo == 'ingreso': self.cuenta.saldo += self.monto
            else: self.cuenta.saldo -= self.monto
            self.cuenta.save()
        super().save(*args, **kwargs)

class Caja(models.Model):
    nombre = models.CharField(max_length=100)
    responsable = models.ForeignKey(User, on_delete=models.PROTECT)
    monto_asignado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    activa = models.BooleanField(default=True)
    def __str__(self): return self.nombre

class MovimientoCaja(models.Model):
    TIPO_M_CHOICES = [('ingreso', 'Ingreso'), ('egreso', 'Egreso')]
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name="movimientos")
    fecha = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPO_M_CHOICES)
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    comprobante = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.tipo == 'ingreso': self.caja.saldo += self.monto
            else: self.caja.saldo -= self.monto
            self.caja.save()
        super().save(*args, **kwargs)

class CuentaPorCobrar(models.Model):
    cliente_nombre = models.CharField(max_length=200, null=True)
    cliente_ruc = models.CharField(max_length=20, blank=True, null=True)
    concepto = models.CharField(max_length=200, null=True)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=15, default='pendiente') # pendiente, parcial, cobrado
    observaciones = models.TextField(blank=True, null=True)

class CuentaPorPagar(models.Model):
    proveedor_nombre = models.CharField(max_length=200, null=True)
    proveedor_ruc = models.CharField(max_length=20, blank=True, null=True)
    concepto = models.CharField(max_length=200, null=True)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=15, default='pendiente') # pendiente, parcial, pagado
    observaciones = models.TextField(blank=True, null=True)

class Cobro(models.Model):
    cxc = models.ForeignKey(CuentaPorCobrar, on_delete=models.CASCADE, related_name="cobros")
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    medio_pago = models.CharField(max_length=50)
    cuenta_bancaria = models.ForeignKey(CuentaBancaria, on_delete=models.SET_NULL, null=True, blank=True)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

class Pago(models.Model):
    cxp = models.ForeignKey(CuentaPorPagar, on_delete=models.CASCADE, related_name="pagos")
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    medio_pago = models.CharField(max_length=50)
    cuenta_bancaria = models.ForeignKey(CuentaBancaria, on_delete=models.SET_NULL, null=True, blank=True)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

class TransferenciaBancaria(models.Model):
    cuenta_origen = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE, related_name="transferencias_salida", null=True)
    cuenta_destino = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE, related_name="transferencias_entrada", null=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.TextField(blank=True, null=True)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    ejecutada = models.BooleanField(default=False)