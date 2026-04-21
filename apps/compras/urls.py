# apps/compras/urls.py
from django.urls import path
from . import views

app_name = "compras"

urlpatterns = [
    # Dashboard
    path("",                                         views.dashboard_compras,          name="dashboard"),

    # Categorías de Proveedor
    path("cat-proveedores/",                         views.categoria_proveedor_list,   name="categoria_proveedor_list"),
    path("cat-proveedores/nueva/",                   views.categoria_proveedor_create, name="categoria_proveedor_create"),
    path("cat-proveedores/<int:pk>/editar/",         views.categoria_proveedor_edit,   name="categoria_proveedor_edit"),

    # Proveedores
    path("proveedores/",                             views.proveedor_list,             name="proveedor_list"),
    path("proveedores/nuevo/",                       views.proveedor_create,           name="proveedor_create"),
    path("proveedores/<int:pk>/",                    views.proveedor_detail,           name="proveedor_detail"),
    path("proveedores/<int:pk>/editar/",             views.proveedor_edit,             name="proveedor_edit"),
    path("proveedores/<int:pk>/contacto/nuevo/",     views.proveedor_contacto_add,     name="proveedor_contacto_add"),
    path("proveedores/<int:pk>/contacto/<int:cpk>/eliminar/",
         views.proveedor_contacto_delete,            name="proveedor_contacto_delete"),

    # Productos
    path("productos/",                               views.producto_list,              name="producto_list"),
    path("productos/nuevo/",                         views.producto_create,            name="producto_create"),
    path("productos/<int:pk>/editar/",               views.producto_edit,              name="producto_edit"),

    # Órdenes de Compra
    path("ordenes/",                                 views.orden_list,                 name="orden_list"),
    path("ordenes/nueva/",                           views.orden_create,               name="orden_create"),
    path("ordenes/<int:pk>/",                        views.orden_detail,               name="orden_detail"),
    path("ordenes/<int:pk>/editar/",                 views.orden_edit,                 name="orden_edit"),
    path("ordenes/<int:pk>/agregar-item/",           views.orden_agregar_detalle,      name="orden_agregar_detalle"),
    path("ordenes/<int:pk>/item/<int:dpk>/eliminar/",views.orden_eliminar_detalle,     name="orden_eliminar_detalle"),
    path("ordenes/<int:pk>/enviar/",                 views.orden_enviar,               name="orden_enviar"),
    path("ordenes/<int:pk>/confirmar/",              views.orden_confirmar,            name="orden_confirmar"),
    path("ordenes/<int:pk>/anular/",                 views.orden_anular,               name="orden_anular"),

    # Recepciones
    path("recepciones/",                             views.recepcion_list,             name="recepcion_list"),
    path("ordenes/<int:orden_pk>/recepcion/nueva/",  views.recepcion_create,           name="recepcion_create"),
    path("recepciones/<int:pk>/",                    views.recepcion_detail,           name="recepcion_detail"),
    path("recepciones/<int:pk>/agregar/",            views.recepcion_agregar_detalle,  name="recepcion_agregar_detalle"),
    path("recepciones/<int:pk>/aprobar/",            views.recepcion_aprobar,          name="recepcion_aprobar"),
]
