from django.db import models

class CategoriaProveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    def __str__(self): return self.nombre

class Proveedor(models.Model):
    ruc = models.CharField(max_length=20, unique=True)
    razon_social = models.CharField(max_length=200)
    nombre_comercial = models.CharField(max_length=200, blank=True, null=True)
    tipo = models.CharField(max_length=20, default='empresa')
    categoria = models.ForeignKey(CategoriaProveedor, on_delete=models.SET_NULL, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=10, default='activo')
    creado_en = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.razon_social
    def nombre_display(self): return self.nombre_comercial or self.razon_social

class ContactoProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="contactos")
    nombre    = models.CharField(max_length=150)
    cargo     = models.CharField(max_length=100, blank=True)
    telefono  = models.CharField(max_length=30, blank=True)
    email     = models.EmailField(blank=True)
    principal = models.BooleanField(default=False)

    def __str__(self): return f"{self.nombre} ({self.proveedor})"

class CategoriaProductoCompra(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self): return self.nombre

class ProductoCompra(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, blank=True)
    categoria = models.ForeignKey(CategoriaProductoCompra, on_delete=models.SET_NULL, null=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def __str__(self): return self.nombre

class OrdenCompra(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('enviada', 'Enviada'),
        ('confirmada', 'Confirmada'),
        ('recibida', 'Recibida'),
        ('completada', 'Completada'),
        ('anulada', 'Anulada'),
    ]
    numero = models.CharField(max_length=20, unique=True, blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor, related_name='ordenes', on_delete=models.PROTECT)
    fecha_emision = models.DateField(auto_now_add=True)
    fecha_entrega = models.DateField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    impuesto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Orden {self.numero or self.id} - {self.proveedor}"

class DetalleOrdenCompra(models.Model):
    orden = models.ForeignKey(OrdenCompra, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(ProductoCompra, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_recibida = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def subtotal(self): return self.cantidad * self.precio_unitario

    @property
    def pendiente_recibir(self): return self.cantidad - self.cantidad_recibida

class RecepcionCompra(models.Model):
    orden = models.ForeignKey(OrdenCompra, related_name='recepciones', on_delete=models.CASCADE)
    numero = models.CharField(max_length=20, unique=True)
    fecha_recepcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='pendiente')

class DetalleRecepcion(models.Model):
    recepcion = models.ForeignKey(RecepcionCompra, related_name='detalles', on_delete=models.CASCADE)
    detalle_orden = models.ForeignKey(DetalleOrdenCompra, on_delete=models.CASCADE)
    cantidad_aceptada = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.CharField(max_length=200, blank=True)