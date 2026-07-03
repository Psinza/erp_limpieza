from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.core_urls if hasattr(admin.site, 'core_urls') else admin.site.urls),
    
    # Autenticación
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    
    # Módulos del Sistema
    path('', include('apps.core.urls', namespace='core')),
    path('administracion/', include('apps.administracion.urls', namespace='administracion')),
    path('rrhh/', include('apps.rrhh.urls', namespace='rrhh')),
    path('contabilidad/', include('apps.contabilidad.urls', namespace='contabilidad')),
    path('vendedores/', include('apps.vendedores.urls', namespace='vendedores')),
    path('compras/', include('apps.compras.urls', namespace='compras')),
    path('ventas/', include('apps.ventas.urls', namespace='ventas')),
    path('activos_fijos/', include('apps.activos_fijos.urls', namespace='activos_fijos')),
    path('ordenacion_pagos/', include('apps.ordenacion_pagos.urls', namespace='ordenacion_pagos')),
    path('comercializacion/', include('apps.comercializacion.urls', namespace='comercializacion')),
    path('produccion/', include('apps.produccion.urls', namespace='produccion')),
    path('logistica/', include('apps.logistica.urls', namespace='logistica')),
    path('facturacion/', include('apps.facturacion.urls', namespace='facturacion')),
    path('viaticos/', include('apps.viaticos.urls', namespace='viaticos')),
    path('transportes/', include('apps.transportes.urls', namespace='transportes')),
    path('tesoreria/', include('apps.tesoreria.urls', namespace='tesoreria')),
    path('inventarios/', include('apps.inventarios.urls', namespace='inventarios')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
