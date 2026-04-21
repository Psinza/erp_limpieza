# Módulo COMPRAS — ERP Fábrica de Limpieza
## Django + PostgreSQL | Bootstrap 5 + Bootstrap Icons

---

## 📦 Estructura del módulo

```
apps/compras/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── urls.py
├── views.py
├── migrations/
│   └── __init__.py
└── templates/compras/
    ├── dashboard_compras.html
    ├── categoria_proveedor_list.html
    ├── categoria_proveedor_form.html
    ├── proveedor_list.html
    ├── proveedor_form.html
    ├── proveedor_detail.html
    ├── contacto_form.html
    ├── producto_list.html
    ├── producto_form.html
    ├── orden_list.html
    ├── orden_form.html
    ├── orden_detail.html
    ├── recepcion_list.html
    ├── recepcion_form.html
    └── recepcion_detail.html
```

---

## 🗃️ Modelos

| Modelo                    | Campos clave                                                  |
|---------------------------|---------------------------------------------------------------|
| `CategoriaProveedor`      | nombre, descripcion                                           |
| `Proveedor`               | ruc, razon_social, tipo, categoria, dias_credito, estado      |
| `ContactoProveedor`       | proveedor, nombre, cargo, telefono, email, principal          |
| `CategoriaProductoCompra` | nombre, descripcion                                           |
| `ProductoCompra`          | codigo, nombre, unidad_medida, precio_referencia, stock_minimo|
| `OrdenCompra`             | numero, proveedor, fecha_emision, estado, subtotal, total     |
| `DetalleOrdenCompra`      | orden, producto, cantidad, precio_unitario, descuento, subtotal|
| `RecepcionCompra`         | orden, numero, fecha_recepcion, nro_factura, estado           |
| `DetalleRecepcion`        | recepcion, detalle_orden, cantidad_recibida, aceptada, rechazada|

---

## 🔄 Flujo de Orden de Compra

```
Borrador → [Enviar] → Enviada → [Confirmar] → Confirmada
                                      ↓
                              [Registrar Recepción]
                                      ↓
                              Recibida Parcialmente
                                      ↓
                         (todas recibidas) → Completada
                               (cualquier estado) → [Anular] → Anulada
```

---

## ⚙️ Instalación

### 1. Copiar el módulo
```
Copiar la carpeta apps/compras/ dentro de tu proyecto Django.
```

### 2. Registrar en settings.py
```python
INSTALLED_APPS = [
    ...
    'apps.core',
    'apps.rrhh',
    'apps.compras',   # ← agregar
]
```

### 3. Registrar URLs en config/urls.py
```python
path('compras/', include('apps.compras.urls', namespace='compras')),
```

### 4. Ejecutar migraciones
```bash
python manage.py makemigrations compras
python manage.py migrate
```

---

## 🔗 URLs disponibles (28 rutas)

| Nombre                            | URL                                           |
|-----------------------------------|-----------------------------------------------|
| `compras:dashboard`               | /compras/                                     |
| `compras:categoria_proveedor_list`| /compras/cat-proveedores/                     |
| `compras:proveedor_list`          | /compras/proveedores/                         |
| `compras:proveedor_create`        | /compras/proveedores/nuevo/                   |
| `compras:proveedor_detail`        | /compras/proveedores/<pk>/                    |
| `compras:proveedor_edit`          | /compras/proveedores/<pk>/editar/             |
| `compras:proveedor_contacto_add`  | /compras/proveedores/<pk>/contacto/nuevo/     |
| `compras:producto_list`           | /compras/productos/                           |
| `compras:producto_create`         | /compras/productos/nuevo/                     |
| `compras:producto_edit`           | /compras/productos/<pk>/editar/               |
| `compras:orden_list`              | /compras/ordenes/                             |
| `compras:orden_create`            | /compras/ordenes/nueva/                       |
| `compras:orden_detail`            | /compras/ordenes/<pk>/                        |
| `compras:orden_agregar_detalle`   | /compras/ordenes/<pk>/agregar-item/           |
| `compras:orden_eliminar_detalle`  | /compras/ordenes/<pk>/item/<dpk>/eliminar/    |
| `compras:orden_enviar`            | /compras/ordenes/<pk>/enviar/                 |
| `compras:orden_confirmar`         | /compras/ordenes/<pk>/confirmar/              |
| `compras:orden_anular`            | /compras/ordenes/<pk>/anular/                 |
| `compras:recepcion_list`          | /compras/recepciones/                         |
| `compras:recepcion_create`        | /compras/ordenes/<pk>/recepcion/nueva/        |
| `compras:recepcion_detail`        | /compras/recepciones/<pk>/                    |
| `compras:recepcion_agregar_detalle`| /compras/recepciones/<pk>/agregar/           |
| `compras:recepcion_aprobar`       | /compras/recepciones/<pk>/aprobar/            |

---

## 📝 Próximos módulos
- `apps/ventas/`     — Pedidos, Clientes
- `apps/produccion/` — Fórmulas, Lotes, Productos terminados
- `apps/tesoreria/`  — Flujo de caja, Bancos
