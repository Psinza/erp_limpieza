from django.urls import path
from . import views

app_name = 'contabilidad'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('asientos/', views.asiento_list, name='asiento_list'),
    path('asientos/nuevo/', views.asiento_create, name='asiento_create'),
    path('asientos/<int:pk>/', views.asiento_detail, name='asiento_detail'),
    path('asientos/<int:pk>/aprobar/', views.asiento_aprobar, name='asiento_aprobar'),
    path('asientos/<int:pk>/anular/', views.asiento_anular, name='asiento_anular'),
    path('asientos/<int:pk>/agregar-linea/', views.asiento_agregar_linea, name='asiento_agregar_linea'),
    path('asientos/<int:pk>/eliminar-linea/<int:linea_pk>/', views.asiento_eliminar_linea, name='asiento_eliminar_linea'),
    path('plan-cuentas/', views.plan_cuentas, name='plan_cuentas'),
    path('cuentas/nueva/', views.cuenta_create, name='cuenta_create'),
    path('cuentas/<int:pk>/editar/', views.cuenta_update, name='cuenta_edit'),
    path('ejercicios/', views.ejercicio_list, name='ejercicio_list'),
    path('ejercicios/nuevo/', views.ejercicio_create, name='ejercicio_create'),
    path('ejercicios/<int:pk>/cerrar/', views.ejercicio_cerrar, name='ejercicio_cerrar'),
    path('libro-diario/', views.libro_diario, name='libro_diario'),
    path('libro-ventas/', views.libro_ventas, name='libro_ventas'),
    path('balance-general/', views.balance_general, name='balance_general'),
    path('balance-general/pdf/', views.balance_general, name='balance_general_pdf'),
    path('estado-resultados/', views.estado_resultados, name='estado_resultados'),
    path('estado-resultados/pdf/', views.estado_resultados, name='estado_resultados_pdf'),
    path('balance-comprobacion/', views.balance_comprobacion, name='balance_comprobacion'),
    path('cuenta-mayor/', views.cuenta_mayor, name='cuenta_mayor'),
]