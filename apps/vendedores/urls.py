from django.urls import path
from apps.core.views import modulo_en_construccion

app_name = 'vendedores'

urlpatterns = [
    # Pasamos 'Vendedores' como parámetro adicional directamente desde la URL
    path('', modulo_en_construccion, {'nombre_modulo': 'Vendedores'}, name='dashboard'),
]