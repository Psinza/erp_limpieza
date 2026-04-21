# apps/tesoreria/admin.py
from django.contrib import admin
from .models import (
    Banco, CuentaBancaria, MovimientoBancario,
    Caja, MovimientoCaja,
    CuentaPorCobrar, CuentaPorPagar,
    Cobro, Pago, TransferenciaBancaria
)

@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'pais', 'activo')

@admin.register(CuentaBancaria)
class CuentaBancariaAdmin(admin.ModelAdmin):
    list_display = ('banco', 'numero', 'alias', 'tipo', 'moneda', 'saldo')
    list_filter = ('banco', 'tipo', 'moneda')

@admin.register(MovimientoBancario)
class MovimientoBancarioAdmin(admin.ModelAdmin):
    list_display = ('cuenta', 'fecha', 'tipo', 'concepto', 'monto')
    list_filter = ('tipo', 'cuenta')

@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'responsable', 'saldo', 'activa')

@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    list_display = ('caja', 'fecha', 'tipo', 'monto', 'comprobante')

@admin.register(CuentaPorCobrar)
class CXCAdmin(admin.ModelAdmin):
    list_display = ('cliente_nombre', 'fecha_vencimiento', 'monto_total', 'saldo_pendiente', 'estado')
    list_filter = ('estado',)

@admin.register(CuentaPorPagar)
class CXPAdmin(admin.ModelAdmin):
    list_display = ('proveedor_nombre', 'fecha_vencimiento', 'monto_total', 'saldo_pendiente', 'estado')
    list_filter = ('estado',)

@admin.register(Cobro)
class CobroAdmin(admin.ModelAdmin):
    list_display = ('cxc', 'fecha', 'monto', 'medio_pago')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('cxp', 'fecha', 'monto', 'medio_pago')

@admin.register(TransferenciaBancaria)
class TransferenciaBancariaAdmin(admin.ModelAdmin):
    list_display = ('cuenta_origen', 'cuenta_destino', 'monto', 'fecha', 'ejecutada')
