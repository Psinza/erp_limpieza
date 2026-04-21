from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include('apps.core.urls', namespace='core')),
    # A medida que se agreguen módulos:
    # path('rrhh/', include('apps.rrhh.urls', namespace='rrhh')),
    # path('compras/', include('apps.compras.urls', namespace='compras')),
    # path('ventas/', include('apps.ventas.urls', namespace='ventas')),
    # path('produccion/', include('apps.produccion.urls', namespace='produccion')),
    # path('logistica/', include('apps.logistica.urls', namespace='logistica')),
    # path('tesoreria/', include('apps.tesoreria.urls', namespace='tesoreria')),
    # path('contabilidad/', include('apps.contabilidad.urls', namespace='contabilidad')),
    # path('transportes/', include('apps.transportes.urls', namespace='transportes')),
    # path('vendedores/', include('apps.vendedores.urls', namespace='vendedores')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
