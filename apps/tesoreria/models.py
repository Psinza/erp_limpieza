from django.db import models
from decimal import Decimal
from django.conf import settings

class Banco(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_sudeban = models.CharField(max_length=4, blank=True)
    codigo = models.CharField(max_length=10, blank=True, verbose_name="Código/Sudeban")
    pais = models.CharField(max_length=50, default="Venezuela")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class CuentaBancaria(models.Model):
    TIPO_CUENTA = [('corriente', 'Corriente'), ('ahorro', 'Ahorro')]
    MONEDA = [('VES', 'Bolívares'), ('USD', 'Dólares')]

    banco = models.ForeignKey(Banco, on_delete=models.CASCADE)
    numero = models.CharField(max_length=20)
    alias = models.CharField(max_length=50, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CUENTA, default='corriente')
    moneda = models.CharField(max_length=3, choices=MONEDA, default='VES')
    saldo = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    saldo_inicial = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    titular = models.CharField(max_length=100, blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.banco} - {self.numero}"
        return f"{self.alias or self.banco} - {self.numero[-4:]}"

class Caja(models.Model):
    nombre = models.CharField(max_length=100)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    monto_asignado = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class MovimientoCaja(models.Model):
    TIPO_CHOICES = [('I', 'Ingreso'), ('E', 'Egreso')]
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='movimientos')
    fecha = models.DateField()
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=20, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    comprobante = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.monto} ({self.caja})"

class Pago(models.Model):
    """Modelo de Pago con lógica de Retención de IVA SENIAT (Leyes Venezolanas)."""
    fecha = models.DateField(auto_now_add=True)
    MEDIO_PAGO = [('transferencia', 'Transferencia'), ('efectivo', 'Efectivo'), ('pago_movil', 'Pago Móvil')]
    
    fecha = models.DateField()
    cxp = models.ForeignKey('CuentaPorPagar', on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos')
    monto_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Monto Total Factura")
    monto = models.DecimalField(max_digits=20, decimal_places=2, default=0, help_text="Monto transado")
    monto_base = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Monto Base Imponible")
    monto_iva = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Monto IVA")
    
    # Porcentajes de retención permitidos por el SENIAT
    RETENCION_OPCIONES = [
        (Decimal('0.00'), 'Sin Retención'),
        (Decimal('75.00'), '75% (General)'),
        (Decimal('100.00'), '100% (Casos Especiales)'),
    ]
    porcentaje_retencion = models.DecimalField(
        max_digits=5, decimal_places=2, choices=RETENCION_OPCIONES, default=Decimal('0.00')
    )
    

    monto_retenido = models.DecimalField(max_digits=20, decimal_places=2, editable=False, default=0)
    monto_neto = models.DecimalField(max_digits=20, decimal_places=2, editable=False, default=0)
    
    medio_pago = models.CharField(max_length=20, choices=MEDIO_PAGO, default='transferencia')
    cuenta_bancaria = models.ForeignKey(CuentaBancaria, on_delete=models.SET_NULL, null=True, blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Cálculo automático de la retención de IVA según providencia SENIAT
        if self.monto_iva > 0 and self.porcentaje_retencion > 0:
            self.monto_retenido = (self.monto_iva * self.porcentaje_retencion) / Decimal('100.00')
        else:
            self.monto_retenido = Decimal('0.00')
        
        if self.monto == 0:
            self.monto = self.monto_total
        self.monto_neto = self.monto_total - self.monto_retenido
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

class CuentaPorCobrar(models.Model):
    ESTADOS = [('pendiente', 'Pendiente'), ('parcial', 'Pago Parcial'), ('pagada', 'Pagada')]
    cliente_nombre = models.CharField(max_length=200)
    cliente_ruc = models.CharField(max_length=20, blank=True)
    concepto = models.CharField(max_length=200)
    referencia = models.CharField(max_length=100, blank=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    monto_total = models.DecimalField(max_digits=20, decimal_places=2)
    saldo_pendiente = models.DecimalField(max_digits=20, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"CXC {self.cliente_nombre} - {self.monto_total}"

class CuentaPorPagar(models.Model):
    ESTADOS = [('pendiente', 'Pendiente'), ('parcial', 'Pago Parcial'), ('pagada', 'Pagada')]
    proveedor_nombre = models.CharField(max_length=200)
    proveedor_ruc = models.CharField(max_length=20, blank=True)
    concepto = models.CharField(max_length=200)
    referencia = models.CharField(max_length=100, blank=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    monto_total = models.DecimalField(max_digits=20, decimal_places=2)
    saldo_pendiente = models.DecimalField(max_digits=20, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"CXP {self.proveedor_nombre} - {self.monto_total}"

class Cobro(models.Model):
    MEDIO_PAGO = [('transferencia', 'Transferencia'), ('efectivo', 'Efectivo'), ('pago_movil', 'Pago Móvil')]
    cxc = models.ForeignKey(CuentaPorCobrar, on_delete=models.CASCADE, related_name='cobros')
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=20, decimal_places=2)
    medio_pago = models.CharField(max_length=20, choices=MEDIO_PAGO)
    cuenta_bancaria = models.ForeignKey(CuentaBancaria, on_delete=models.SET_NULL, null=True, blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Cobro {self.monto} - {self.cxc.cliente_nombre}"

class MovimientoBancario(models.Model):
    TIPO_CHOICES = [('I', 'Ingreso'), ('E', 'Egreso')]
    
    CONCEPTO_CHOICES = [('pago', 'Pago'), ('cobro', 'Cobro'), ('transferencia', 'Transferencia'), ('ajuste', 'Ajuste')]

    cuenta = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE, related_name='movimientos')
    pago = models.ForeignKey(Pago, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_bancarios')
    concepto = models.CharField(max_length=20, choices=CONCEPTO_CHOICES, default='ajuste')
    fecha = models.DateField()
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=20, decimal_places=2)
    monto_igtf = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0.00"), help_text="Monto retenido por IGTF (si aplica)")
    descripcion = models.CharField(max_length=255)
    referencia = models.CharField(max_length=100, blank=True)
    conciliado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.monto} - {self.cuenta}"

    class Meta:
        verbose_name = "Movimiento Bancario"
        verbose_name_plural = "Movimientos Bancarios"

class TransferenciaBancaria(models.Model):
    cuenta_origen = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE, related_name='transferencias_realizadas')
    cuenta_destino = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE, related_name='transferencias_recibidas')
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=20, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    referencia = models.CharField(max_length=100, blank=True)
    ejecutada = models.BooleanField(default=True)

    def __str__(self):
        return f"Trf {self.monto}: {self.cuenta_origen} -> {self.cuenta_destino}"

class ConciliacionBancaria(models.Model):
    cuenta = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE, related_name='conciliaciones')
    mes = models.IntegerField(choices=[(i, str(i)) for i in range(1, 13)])
    anio = models.IntegerField()
    saldo_estado_cuenta = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'), help_text="Saldo final en el estado de cuenta del banco")
    saldo_libros = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'), help_text="Saldo final en el sistema")
    fecha_cierre = models.DateField()
    cerrada = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Conciliación Bancaria"
        verbose_name_plural = "Conciliaciones Bancarias"
        unique_together = ('cuenta', 'mes', 'anio')

    def diferencia(self):
        return self.saldo_estado_cuenta - self.saldo_libros

    def __str__(self):
        return f"Conciliación {self.cuenta.banco.nombre} - {self.mes}/{self.anio}"