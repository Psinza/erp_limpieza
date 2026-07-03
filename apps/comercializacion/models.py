from django.db import models
from apps.produccion.models import ProductoTerminado

class CategoriaComercial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    imagen = models.FileField(upload_to='comercial/categorias/', null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías Comerciales"

class InformacionComercial(models.Model):
    """Información extendida del producto para el catálogo (Marketing)"""
    producto = models.OneToOneField(ProductoTerminado, on_delete=models.CASCADE, related_name='info_comercial')
    categoria = models.ForeignKey(CategoriaComercial, on_delete=models.SET_NULL, null=True, related_name='productos')
    nombre_comercial = models.CharField(max_length=255)
    descripcion_larga = models.TextField(help_text="Descripción detallada para catálogos o web")
    ficha_tecnica = models.FileField(upload_to='comercial/fichas/', null=True, blank=True)
    en_oferta = models.BooleanField(default=False)
    destacado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre_comercial

class ListaPrecio(models.Model):
    """Diferentes listas de precios (PVP, Mayorista, Distribuidor, etc.)"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    moneda = models.CharField(max_length=10, default='USD')
    factor_ajuste = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, help_text="Factor multiplicador global (opcional)")

    def __str__(self):
        return f"{self.nombre} ({self.moneda})"

class ItemPrecio(models.Model):
    lista = models.ForeignKey(ListaPrecio, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(ProductoTerminado, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    descuento_maximo = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('lista', 'producto')

    def __str__(self):
        return f"{self.producto.nombre} en {self.lista.nombre}"