from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

# Asumiendo que Cliente y ProductoVenta ya existen o se definirán aquí.
# Si ya existen en otro archivo, se importarían.

class CategoriaCliente(models.Model):
    nombre          = models.CharField(max_length=100, unique=True)
    descuento_pct   = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name="Descuento (%)")
    descripcion     = models.TextField(blank=True)

    class Meta:
        verbose_name = "Categoría de Cliente"
        verbose_name_plural = "Categorías de Clientes"

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    id              = models.AutoField(primary_key=True)
    rif             = models.CharField(max_length=20, unique=True, verbose_name="RIF/Documento")
    razon_social    = models.CharField(max_length=200, verbose_name="Razón Social")
    nombre_comercial= models.CharField(max_length=200, blank=True)
    tipo            = models.CharField(max_length=20, default='juridico')
    categoria       = models.ForeignKey(CategoriaCliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='clientes')
    direccion       = models.TextField(blank=True)
    telefono        = models.CharField(max_length=20, blank=True)
    email           = models.EmailField(max_length=254, blank=True)
    estado          = models.CharField(max_length=10, default='activo')
    creado_en       = models.DateTimeField(default=timezone.now)
    modificado_en   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.razon_social

class ContactoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contactos')
    nombre = models.CharField(max_length=200)
    cargo = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    principal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} ({self.cliente.razon_social})"

class CategoriaProductoVenta(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class ProductoVenta(models.Model):
    id                  = models.AutoField(primary_key=True)
    codigo              = models.CharField(max_length=50, unique=True, blank=True)
    nombre              = models.CharField(max_length=200)
    categoria           = models.ForeignKey(CategoriaProductoVenta, on_delete=models.SET_NULL, null=True, blank=True)
    producto_base_id    = models.IntegerField(null=True, blank=True) # Vínculo con Producción
    precio_venta        = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    impuesto_pct        = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('16.00'))
    moneda              = models.CharField(max_length=5, default='USD')
    activo              = models.BooleanField(default=True)
    tipo_producto       = models.CharField(max_length=50, blank=True) # Limpieza Hogar, Industrial, etc.

    def __str__(self):
        return self.nombre

class Cotizacion(models.Model):
    numero = models.CharField(max_length=20, unique=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_emision = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=20, default='borrador')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    base_imponible = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuesto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    def __str__(self): return f"COT-{self.numero}"

class DetalleCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(ProductoVenta, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descuento_monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    numero = models.CharField(max_length=20, unique=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    fecha_pedido = models.DateField(default=timezone.now)
    dias_credito = models.PositiveIntegerField(default=0)
    direccion_despacho = models.TextField(blank=True, verbose_name="Dirección de Despacho")
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('16.00'), verbose_name="IVA (%)")
    descuento_global_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name="Desc. Global (%)")
    descuento_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    base_imponible = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    impuesto_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='borrador')
    observaciones = models.TextField(blank=True)

    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='pedidos_creados')
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_pedido', '-creado_en']

    def __str__(self):
        return f"Pedido {self.numero} - {self.cliente.razon_social}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.generar_numero()
        self.calcular_totales()
        super().save(*args, **kwargs)

    def calcular_totales(self):
        self.subtotal = sum(item.subtotal for item in self.items.all())
        # Apply global discount to subtotal first
        subtotal_con_descuento = self.subtotal * (Decimal('100.00') - self.descuento_global_porcentaje) / Decimal('100.00')
        self.descuento_total = self.subtotal - subtotal_con_descuento
        self.base_imponible = subtotal_con_descuento
        self.impuesto_total = self.base_imponible * (self.iva_porcentaje / Decimal('100.00'))
        self.total = subtotal_con_descuento + self.impuesto_total

    @classmethod
    def generar_numero(cls):
        year = timezone.now().year
        last_pedido = cls.objects.filter(numero__startswith=str(year)).order_by('-numero').first()
        seq = 1
        if last_pedido:
            try:
                seq = int(last_pedido.numero.split('-')[-1]) + 1
            except (ValueError, IndexError):
                pass
        return f"PED-{year}-{seq:04d}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(ProductoVenta, on_delete=models.PROTECT, related_name='detalle_pedidos')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
    cantidad_despachada = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    descuento_monto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedido"
        unique_together = ['pedido', 'producto']

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido {self.pedido.numero}"

    def save(self, *args, **kwargs):
        bruto = self.cantidad * self.precio_unitario
        self.descuento_monto = bruto * (self.descuento_pct / Decimal('100.00'))
        self.subtotal = bruto - self.descuento_monto
        super().save(*args, **kwargs)
        # Recalcular y guardar los totales del pedido padre
        self.pedido.calcular_totales()
        self.pedido.save()

class Despacho(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    fecha_despacho = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, default='pendiente')
    despachado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

class DetalleDespacho(models.Model):
    despacho = models.ForeignKey(Despacho, on_delete=models.CASCADE, related_name='detalles')
    detalle_pedido = models.ForeignKey(DetallePedido, on_delete=models.CASCADE)
    cantidad_despachada = models.DecimalField(max_digits=12, decimal_places=2)
    observacion = models.TextField(blank=True)