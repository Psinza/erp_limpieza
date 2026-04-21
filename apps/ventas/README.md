# Módulo VENTAS — ERP Fábrica de Limpieza
## Django + PostgreSQL | Bootstrap 5 + Bootstrap Icons

---

## 📦 Estructura del módulo

```
apps/ventas/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── urls.py
├── views.py
├── migrations/
│   └── __init__.py
└── templates/ventas/
    ├── dashboard_ventas.html
    ├── categoria_cliente_list.html
    ├── categoria_cliente_form.html
    ├── cliente_list.html
    ├── cliente_form.html
    ├── cliente_detail.html
    ├── contacto_cliente_form.html
    ├── producto_list.html
    ├── producto_form.html
    ├── cotizacion_list.html
    ├── cotizacion_form.html
    ├── cotizacion_detail.html
    ├── pedido_list.html
    ├── pedido_form.html
    ├── pedido_detail.html
    ├── despacho_list.html
    ├── despacho_form.html
    └── despacho_detail.html
```

---

## 🗃️ Modelos

| Modelo                  | Descripción                                          |
|-------------------------|------------------------------------------------------|
| `CategoriaCliente`      | Agrupación de clientes con descuento por defecto     |
| `Cliente`               | Datos fiscales, condiciones, vendedor asignado       |
| `ContactoCliente`       | Personas de contacto por cliente                     |
| `CategoriaProductoVenta`| Agrupación de productos                              |
| `ProductoVenta`         | Código, precio venta, precio mínimo, IVA             |
| `Cotizacion`            | Propuesta comercial con ítems y totales              |
| `DetalleCotizacion`     | Líneas de cotización con descuentos                  |
| `Pedido`                | Orden de venta confirmada, vinculable a cotización   |
| `DetallePedido`         | Líneas del pedido con control de despacho            |
| `Despacho`              | Registro de entrega física del pedido                |
| `DetalleDespacho`       | Cantidades despachadas por ítem                      |

---

## 🔄 Flujos implementados

### Cotización
```
Borrador → [Enviar] → Enviada → [Aceptar] → Aceptada → [Convertir] → Convertida a Pedido
                              → [Rechazar] → Rechazada
```

### Pedido
```
Borrador → [Confirmar] → Confirmado → [En Proceso] → En Proceso
                                    → [Crear Despacho] → Despachado → Entregado
```

### Despacho
```
Preparando → [Agregar ítems] → [Marcar Entregado] → Entregado
```

---

## ⚙️ Instalación

### 1. settings.py
```python
INSTALLED_APPS = [
    ...
    'apps.core',
    'apps.rrhh',
    'apps.compras',
    'apps.ventas',   # ← agregar
]
```

### 2. config/urls.py
```python
path('ventas/', include('apps.ventas.urls', namespace='ventas')),
```

### 3. Migrar
```bash
python manage.py makemigrations ventas
python manage.py migrate
```

---

## 🔗 URLs disponibles (40 rutas)

| Grupo         | Rutas                                                         |
|---------------|---------------------------------------------------------------|
| Dashboard     | `/ventas/`                                                    |
| Categorías    | `/ventas/cat-clientes/`  nueva / editar                       |
| Clientes      | lista / nuevo / detalle / editar / contacto                   |
| Productos     | lista / nuevo / editar                                        |
| Cotizaciones  | lista / nueva / detalle / editar / ítems / enviar / aceptar / rechazar / convertir |
| Pedidos       | lista / nuevo / detalle / editar / ítems / confirmar / en-proceso / anular |
| Despachos     | lista / nuevo / detalle / agregar-ítem / entregar             |

---

## 📝 Próximos módulos
- `apps/produccion/`    — Fórmulas, Lotes, Productos terminados
- `apps/tesoreria/`     — Flujo de caja, Bancos
- `apps/contabilidad/`  — Asientos, Balances
- `apps/transportes/`   — Rutas, Vehículos
