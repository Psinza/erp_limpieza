# apps/transportes/forms.py
from django import forms
from django.utils import timezone
from .models import (
    TipoVehiculo, Vehiculo, Conductor,
    Zona, Ruta, PuntoEntrega,
    Despacho, EntregaDespacho, Mantenimiento,
)

CTR  = {"class": "form-control"}
SEL  = {"class": "form-select"}
NUM  = {"class": "form-control", "step": "0.01"}
DATE = {"class": "form-control", "type": "date"}
DTTM = {"class": "form-control", "type": "datetime-local"}
CHK  = {"class": "form-check-input"}
TXT  = {"class": "form-control", "rows": 3}


class TipoVehiculoForm(forms.ModelForm):
    class Meta:
        model   = TipoVehiculo
        fields  = ["nombre", "descripcion"]
        widgets = {
            "nombre":      forms.TextInput(attrs=CTR),
            "descripcion": forms.Textarea(attrs=TXT),
        }


class VehiculoForm(forms.ModelForm):
    class Meta:
        model  = Vehiculo
        fields = [
            "placa", "tipo", "marca", "modelo", "año", "color",
            "combustible", "capacidad_carga", "capacidad_volumen",
            "odometro", "estado",
            "soat_vencimiento", "revision_vencimiento", "seguro_vencimiento",
            "certificado_registro", "poliza_rcv", "permiso_carga", "permiso_carga_vencimiento",
            "foto", "observaciones",
        ]
        widgets = {
            "placa":               forms.TextInput(attrs=CTR),
            "tipo":                forms.Select(attrs=SEL),
            "marca":               forms.TextInput(attrs=CTR),
            "modelo":              forms.TextInput(attrs=CTR),
            "año":                 forms.NumberInput(attrs=CTR),
            "color":               forms.TextInput(attrs=CTR),
            "combustible":         forms.Select(attrs=SEL),
            "capacidad_carga":     forms.NumberInput(attrs=NUM),
            "capacidad_volumen":   forms.NumberInput(attrs=NUM),
            "odometro":            forms.NumberInput(attrs=NUM),
            "estado":              forms.Select(attrs=SEL),
            "soat_vencimiento":    forms.DateInput(attrs=DATE),
            "revision_vencimiento":forms.DateInput(attrs=DATE),
            "seguro_vencimiento":  forms.DateInput(attrs=DATE),
            "certificado_registro": forms.TextInput(attrs=CTR),
            "poliza_rcv":           forms.TextInput(attrs=CTR),
            "permiso_carga":        forms.TextInput(attrs=CTR),
            "permiso_carga_vencimiento": forms.DateInput(attrs=DATE),
            "foto":                forms.ClearableFileInput(attrs=CTR),
            "observaciones":       forms.Textarea(attrs=TXT),
        }


class ConductorForm(forms.ModelForm):
    class Meta:
        model  = Conductor
        fields = [
            "cedula", "nombres", "apellidos", "telefono", "email", "direccion",
            "numero_licencia", "categoria_licencia", "licencia_vencimiento",
            "certificado_medico_vencimiento", "curso_carga_pesada", "curso_materiales_peligrosos",
            "estado", "vehiculo_asignado", "foto", "observaciones",
        ]
        widgets = {
            "cedula":              forms.TextInput(attrs=CTR),
            "nombres":             forms.TextInput(attrs=CTR),
            "apellidos":           forms.TextInput(attrs=CTR),
            "telefono":            forms.TextInput(attrs=CTR),
            "email":               forms.EmailInput(attrs=CTR),
            "direccion":           forms.Textarea(attrs={**TXT, "rows": 2}),
            "numero_licencia":     forms.TextInput(attrs=CTR),
            "categoria_licencia":  forms.Select(attrs=SEL),
            "licencia_vencimiento":forms.DateInput(attrs=DATE),
            "certificado_medico_vencimiento": forms.DateInput(attrs=DATE),
            "curso_carga_pesada": forms.CheckboxInput(attrs=CHK),
            "curso_materiales_peligrosos": forms.CheckboxInput(attrs=CHK),
            "estado":              forms.Select(attrs=SEL),
            "vehiculo_asignado":   forms.Select(attrs=SEL),
            "foto":                forms.ClearableFileInput(attrs=CTR),
            "observaciones":       forms.Textarea(attrs=TXT),
        }


class ZonaForm(forms.ModelForm):
    class Meta:
        model   = Zona
        fields  = ["nombre", "descripcion", "activa"]
        widgets = {
            "nombre":      forms.TextInput(attrs=CTR),
            "descripcion": forms.Textarea(attrs=TXT),
            "activa":      forms.CheckboxInput(attrs=CHK),
        }


class RutaForm(forms.ModelForm):
    class Meta:
        model  = Ruta
        fields = [
            "codigo", "nombre", "zona", "origen", "latitud_origen", "longitud_origen", "destino",
            "distancia_km", "tiempo_estimado", "descripcion", "estado",
        ]
        widgets = {
            "codigo":          forms.TextInput(attrs=CTR),
            "nombre":          forms.TextInput(attrs=CTR),
            "zona":            forms.Select(attrs=SEL),
            "origen":          forms.TextInput(attrs=CTR),
            "latitud_origen":  forms.NumberInput(attrs=NUM),
            "longitud_origen": forms.NumberInput(attrs=NUM),
            "destino":         forms.TextInput(attrs=CTR),
            "distancia_km":    forms.NumberInput(attrs=NUM),
            "tiempo_estimado": forms.NumberInput(attrs=CTR),
            "descripcion":     forms.Textarea(attrs=TXT),
            "estado":          forms.Select(attrs=SEL),
        }


class PuntoEntregaForm(forms.ModelForm):
    class Meta:
        model  = PuntoEntrega
        fields = ["orden", "nombre", "direccion", "latitud", "longitud", "cliente_ref", "tiempo_estimado", "activo"]
        widgets = {
            "orden":           forms.NumberInput(attrs=CTR),
            "nombre":          forms.TextInput(attrs=CTR),
            "direccion":       forms.Textarea(attrs={**TXT, "rows": 2}),
            "latitud":         forms.NumberInput(attrs=NUM),
            "longitud":        forms.NumberInput(attrs=NUM),
            "cliente_ref":     forms.TextInput(attrs=CTR),
            "tiempo_estimado": forms.NumberInput(attrs=CTR),
            "activo":          forms.CheckboxInput(attrs=CHK),
        }


class DespachoForm(forms.ModelForm):
    class Meta:
        model  = Despacho
        fields = [
            "ruta", "vehiculo", "conductor",
            "fecha_salida", "fecha_llegada_estimada",
            "numero_guia_despacho", "numero_control_guia", "rif_transportista",
            "descripcion_carga", "peso_carga_kg", "declara_material_peligroso",
            "odometro_salida", "notas",
        ]
        widgets = {
            "ruta":                   forms.Select(attrs=SEL),
            "vehiculo":               forms.Select(attrs=SEL),
            "conductor":              forms.Select(attrs=SEL),
            "fecha_salida":           forms.DateTimeInput(attrs=DTTM),
            "fecha_llegada_estimada": forms.DateTimeInput(attrs=DTTM),
            "numero_guia_despacho":   forms.TextInput(attrs=CTR),
            "numero_control_guia":    forms.TextInput(attrs=CTR),
            "rif_transportista":      forms.TextInput(attrs=CTR),
            "descripcion_carga":      forms.TextInput(attrs=CTR),
            "peso_carga_kg":          forms.NumberInput(attrs=NUM),
            "declara_material_peligroso": forms.CheckboxInput(attrs=CHK),
            "odometro_salida":        forms.NumberInput(attrs=NUM),
            "notas":                  forms.Textarea(attrs=TXT),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehiculo"].queryset = Vehiculo.objects.filter(
            estado="disponible"
        )
        self.fields["conductor"].queryset = Conductor.objects.filter(
            estado="activo",
            licencia_vencimiento__gte=timezone.now().date()
        )
        self.fields["ruta"].queryset = Ruta.objects.filter(estado="activa")


class DespachoFinalizarForm(forms.ModelForm):
    class Meta:
        model  = Despacho
        fields = ["fecha_llegada_real", "odometro_llegada",
                  "combustible_usado", "costo_combustible", "novedad"]
        widgets = {
            "fecha_llegada_real": forms.DateTimeInput(attrs=DTTM),
            "odometro_llegada":   forms.NumberInput(attrs=NUM),
            "combustible_usado":  forms.NumberInput(attrs=NUM),
            "costo_combustible":  forms.NumberInput(attrs=NUM),
            "novedad":            forms.Textarea(attrs=TXT),
        }


class EntregaDespachoForm(forms.ModelForm):
    class Meta:
        model  = EntregaDespacho
        fields = ["punto_entrega", "hora_llegada", "estado",
                  "firma_receptor", "observacion"]
        widgets = {
            "punto_entrega": forms.Select(attrs=SEL),
            "hora_llegada":  forms.DateTimeInput(attrs=DTTM),
            "estado":        forms.Select(attrs=SEL),
            "firma_receptor":forms.TextInput(attrs=CTR),
            "observacion":   forms.Textarea(attrs=TXT),
        }


class MantenimientoForm(forms.ModelForm):
    class Meta:
        model  = Mantenimiento
        fields = [
            "vehiculo", "tipo", "descripcion", "fecha_programada",
            "taller", "km_en_servicio", "km_proximo", "costo", "observaciones",
        ]
        widgets = {
            "vehiculo":         forms.Select(attrs=SEL),
            "tipo":             forms.Select(attrs=SEL),
            "descripcion":      forms.TextInput(attrs=CTR),
            "fecha_programada": forms.DateInput(attrs=DATE),
            "taller":           forms.TextInput(attrs=CTR),
            "km_en_servicio":   forms.NumberInput(attrs=NUM),
            "km_proximo":       forms.NumberInput(attrs=NUM),
            "costo":            forms.NumberInput(attrs=NUM),
            "observaciones":    forms.Textarea(attrs=TXT),
        }
