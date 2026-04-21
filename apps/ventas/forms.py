# apps/ventas/forms.py
from django import forms
from .models import (
    CategoriaCliente, Cliente, ContactoCliente,
    CategoriaProductoVenta, ProductoVenta,
    Cotizacion, DetalleCotizacion,
    Pedido, DetallePedido,
    Despacho, DetalleDespacho,
)

CTR  = {"class": "form-control"}
SEL  = {"class": "form-select"}
NUM  = {"class": "form-control", "step": "0.01"}
NUM4 = {"class": "form-control", "step": "0.0001"}
DATE = {"class": "form-control", "type": "date"}
CHK  = {"class": "form-check-input"}
TXT  = {"class": "form-control", "rows": 3}


class CategoriaClienteForm(forms.ModelForm):
    class Meta:
        model   = CategoriaCliente
        fields  = ["nombre", "descripcion", "descuento_pct"]
        widgets = {
            "nombre":        forms.TextInput(attrs=CTR),
            "descripcion":   forms.Textarea(attrs=TXT),
            "descuento_pct": forms.NumberInput(attrs=NUM),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model  = Cliente
        fields = [
            "ruc", "razon_social", "nombre_comercial", "tipo", "categoria",
            "telefono", "telefono2", "email", "sitio_web",
            "direccion", "ciudad", "pais",
            "dias_credito", "limite_credito", "descuento_pct",
            "vendedor", "observaciones", "estado",
        ]
        widgets = {
            "ruc":             forms.TextInput(attrs=CTR),
            "razon_social":    forms.TextInput(attrs=CTR),
            "nombre_comercial":forms.TextInput(attrs=CTR),
            "tipo":            forms.Select(attrs=SEL),
            "categoria":       forms.Select(attrs=SEL),
            "telefono":        forms.TextInput(attrs=CTR),
            "telefono2":       forms.TextInput(attrs=CTR),
            "email":           forms.EmailInput(attrs=CTR),
            "sitio_web":       forms.URLInput(attrs=CTR),
            "direccion":       forms.Textarea(attrs={**TXT, "rows": 2}),
            "ciudad":          forms.TextInput(attrs=CTR),
            "pais":            forms.TextInput(attrs=CTR),
            "dias_credito":    forms.NumberInput(attrs=CTR),
            "limite_credito":  forms.NumberInput(attrs=NUM),
            "descuento_pct":   forms.NumberInput(attrs=NUM),
            "vendedor":        forms.Select(attrs=SEL),
            "observaciones":   forms.Textarea(attrs=TXT),
            "estado":          forms.Select(attrs=SEL),
        }


class ContactoClienteForm(forms.ModelForm):
    class Meta:
        model   = ContactoCliente
        fields  = ["nombre", "cargo", "telefono", "email", "principal"]
        widgets = {
            "nombre":    forms.TextInput(attrs=CTR),
            "cargo":     forms.TextInput(attrs=CTR),
            "telefono":  forms.TextInput(attrs=CTR),
            "email":     forms.EmailInput(attrs=CTR),
            "principal": forms.CheckboxInput(attrs=CHK),
        }


class CategoriaProductoVentaForm(forms.ModelForm):
    class Meta:
        model   = CategoriaProductoVenta
        fields  = ["nombre", "descripcion"]
        widgets = {
            "nombre":      forms.TextInput(attrs=CTR),
            "descripcion": forms.Textarea(attrs=TXT),
        }


class ProductoVentaForm(forms.ModelForm):
    class Meta:
        model  = ProductoVenta
        fields = [
            "codigo", "nombre", "descripcion", "categoria",
            "unidad_medida", "precio_venta", "precio_minimo",
            "impuesto_pct", "activo",
        ]
        widgets = {
            "codigo":        forms.TextInput(attrs=CTR),
            "nombre":        forms.TextInput(attrs=CTR),
            "descripcion":   forms.Textarea(attrs=TXT),
            "categoria":     forms.Select(attrs=SEL),
            "unidad_medida": forms.Select(attrs=SEL),
            "precio_venta":  forms.NumberInput(attrs=NUM4),
            "precio_minimo": forms.NumberInput(attrs=NUM4),
            "impuesto_pct":  forms.NumberInput(attrs=NUM),
            "activo":        forms.CheckboxInput(attrs=CHK),
        }


class CotizacionForm(forms.ModelForm):
    class Meta:
        model  = Cotizacion
        fields = [
            "cliente", "fecha_emision", "fecha_vencimiento",
            "descuento_pct", "impuesto_pct", "notas", "terminos",
        ]
        widgets = {
            "cliente":           forms.Select(attrs=SEL),
            "fecha_emision":     forms.DateInput(attrs=DATE),
            "fecha_vencimiento": forms.DateInput(attrs=DATE),
            "descuento_pct":     forms.NumberInput(attrs=NUM),
            "impuesto_pct":      forms.NumberInput(attrs=NUM),
            "notas":             forms.Textarea(attrs=TXT),
            "terminos":          forms.Textarea(attrs=TXT),
        }


class DetalleCotizacionForm(forms.ModelForm):
    class Meta:
        model  = DetalleCotizacion
        fields = ["producto", "descripcion", "cantidad", "precio_unitario", "descuento_pct"]
        widgets = {
            "producto":       forms.Select(attrs=SEL),
            "descripcion":    forms.TextInput(attrs=CTR),
            "cantidad":       forms.NumberInput(attrs=NUM),
            "precio_unitario":forms.NumberInput(attrs=NUM4),
            "descuento_pct":  forms.NumberInput(attrs=NUM),
        }


class PedidoForm(forms.ModelForm):
    class Meta:
        model  = Pedido
        fields = [
            "cliente", "fecha_pedido", "fecha_entrega",
            "direccion_entrega", "dias_credito",
            "descuento_pct", "impuesto_pct", "notas",
        ]
        widgets = {
            "cliente":           forms.Select(attrs=SEL),
            "fecha_pedido":      forms.DateInput(attrs=DATE),
            "fecha_entrega":     forms.DateInput(attrs=DATE),
            "direccion_entrega": forms.Textarea(attrs={**TXT, "rows": 2}),
            "dias_credito":      forms.NumberInput(attrs=CTR),
            "descuento_pct":     forms.NumberInput(attrs=NUM),
            "impuesto_pct":      forms.NumberInput(attrs=NUM),
            "notas":             forms.Textarea(attrs=TXT),
        }


class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model  = DetallePedido
        fields = ["producto", "descripcion", "cantidad", "precio_unitario", "descuento_pct"]
        widgets = {
            "producto":       forms.Select(attrs=SEL),
            "descripcion":    forms.TextInput(attrs=CTR),
            "cantidad":       forms.NumberInput(attrs=NUM),
            "precio_unitario":forms.NumberInput(attrs=NUM4),
            "descuento_pct":  forms.NumberInput(attrs=NUM),
        }


class DespachoForm(forms.ModelForm):
    class Meta:
        model  = Despacho
        fields = ["fecha_despacho", "transportista", "numero_guia", "observaciones"]
        widgets = {
            "fecha_despacho": forms.DateInput(attrs=DATE),
            "transportista":  forms.TextInput(attrs=CTR),
            "numero_guia":    forms.TextInput(attrs=CTR),
            "observaciones":  forms.Textarea(attrs=TXT),
        }


class DetalleDespachoForm(forms.ModelForm):
    class Meta:
        model  = DetalleDespacho
        fields = ["detalle_pedido", "cantidad_despachada", "observacion"]
        widgets = {
            "detalle_pedido":      forms.Select(attrs=SEL),
            "cantidad_despachada": forms.NumberInput(attrs=NUM),
            "observacion":         forms.TextInput(attrs=CTR),
        }
