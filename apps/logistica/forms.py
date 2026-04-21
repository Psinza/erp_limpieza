from django import forms
from .models import MovimientoInventario, Almacen
from apps.produccion.models import MateriaPrima, ProductoTerminado

class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = [
            'tipo', 'almacen_origen', 'almacen_destino', 
            'materia_prima', 'producto_pt', 'cantidad', 
            'costo_unitario', 'documento_referencia', 'motivo'
        ]
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        origen = cleaned_data.get('almacen_origen')
        destino = cleaned_data.get('almacen_destino')
        mp = cleaned_data.get('materia_prima')
        pt = cleaned_data.get('producto_pt')

        # Validar que se elija exactamente un tipo de ítem
        if not mp and not pt:
            raise forms.ValidationError("Debe seleccionar una Materia Prima o un Producto Terminado.")
        if mp and pt:
            raise forms.ValidationError("No puede seleccionar ambos (MP y PT) en un mismo movimiento.")

        # Validaciones de Almacenes según el tipo de movimiento
        if tipo == 'E' and not destino:
            self.add_error('almacen_destino', "Para una entrada se requiere un almacén de destino.")
        
        if tipo == 'S' and not origen:
            self.add_error('almacen_origen', "Para una salida se requiere un almacén de origen.")
            
        if tipo == 'T':
            if not origen or not destino:
                raise forms.ValidationError("Para una transferencia se requieren ambos almacenes (origen y destino).")
            if origen == destino:
                raise forms.ValidationError("El almacén de origen y destino no pueden ser el mismo.")

        # Validar stock suficiente para Salidas y Transferencias
        if tipo in ['S', 'T']:
            item = mp if mp else pt
            cantidad = cleaned_data.get('cantidad', 0)
            if item.stock_actual < cantidad:
                raise forms.ValidationError(f"Stock insuficiente. Disponible: {item.stock_actual}")
        
        return cleaned_data