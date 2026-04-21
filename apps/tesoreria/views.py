from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_tesoreria(request):
    # Por ahora usamos el template de construcción
    return render(request, 'core/under_construction.html', {'modulo': 'Tesorería'})

# Agrega placeholders para las otras rutas mencionadas en tus URLs
def banco_list(request): pass
def banco_create(request): pass
# ... (puedes ir completando el resto según necesites)