from django.contrib import admin
from .models import CategoriaComercial, InformacionComercial, ListaPrecio, ItemPrecio

@admin.register(CategoriaComercial)
class CategoriaComercialAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(InformacionComercial)
class InformacionComercialAdmin(admin.ModelAdmin):
    list_display = ('nombre_comercial', 'producto', 'categoria', 'en_oferta', 'destacado')
    list_filter = ('categoria', 'en_oferta', 'destacado')
    search_fields = ('nombre_comercial', 'producto__nombre')

@admin.register(ListaPrecio)
class ListaPrecioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'moneda', 'factor_ajuste', 'activa')
    list_filter = ('moneda', 'activa')

@admin.register(ItemPrecio)
class ItemPrecioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'lista', 'precio', 'descuento_maximo')
    list_filter = ('lista',)
    search_fields = ('producto__nombre_comercial',)
