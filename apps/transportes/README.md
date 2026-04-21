# Módulo TRANSPORTES — ERP Fábrica de Limpieza
## Django + PostgreSQL | Bootstrap 5 + Bootstrap Icons

---

## 📦 Estructura del módulo

```
apps/transportes/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── urls.py
├── views.py
├── migrations/
│   └── __init__.py
└── templates/transportes/
    ├── dashboard_transportes.html
    ├── vehiculo_list.html
    ├── vehiculo_form.html
    ├── vehiculo_detail.html
    ├── conductor_list.html
    ├── conductor_form.html
    ├── conductor_detail.html
    ├── ruta_list.html
    ├── ruta_form.html
    ├── ruta_detail.html
    ├── despacho_list.html
    ├── despacho_form.html
    ├── despacho_detail.html
    ├── mantenimiento_list.html
    └── mantenimiento_form.html
```

---

## 🗃️ Modelos

| Modelo              | Descripción                                                        |
|---------------------|--------------------------------------------------------------------|
| `TipoVehiculo`      | Categoría de vehículo (camión, furgoneta, moto, etc.)             |
| `Vehiculo`          | Flota con estado, odómetro y control de documentos                 |
| `Conductor`         | Chofer con licencia, categoría y vehículo asignado                 |
| `Zona`              | Área geográfica de cobertura                                       |
| `Ruta`              | Trayecto con origen, destino, distancia y tiempo estimado          |
| `PuntoEntrega`      | Parada específica dentro de una ruta (cliente, dirección, orden)   |
| `Despacho`          | Viaje asignando vehículo + conductor + ruta                        |
| `EntregaDespacho`   | Registro de entrega en cada punto durante el despacho              |
| `Mantenimiento`     | Programación y seguimiento de mantenimiento de vehículos           |

---

## 🔄 Flujos implementados

### Despacho
```
Nuevo Despacho → Programado → [Iniciar] → En Ruta
                                              ↓
                                     Actualizar entregas en cada punto
                                              ↓
                                   [Finalizar: km, combustible, costo]
                                              ↓
                              Completado / Con Novedad
                              (Vehículo vuelve a "Disponible" automáticamente)
```

### Mantenimiento
```
Programar → [Vehículo pasa a "En Mantenimiento"]
                        ↓
              [Completar] → Completado
              (Vehículo vuelve a "Disponible" automáticamente)
```

---

## 💡 Automatizaciones implementadas

| Evento | Acción automática |
|--------|-------------------|
| Crear despacho | Vehículo → `en_ruta`, se crean `EntregaDespacho` por cada punto de la ruta |
| Finalizar despacho | Vehículo → `disponible`, se actualiza odómetro |
| Programar mantenimiento | Vehículo → `mantenimiento` |
| Completar mantenimiento | Vehículo → `disponible` |
| Formulario de despacho | Solo muestra vehículos `disponibles` y conductores `activos` |

---

## ⚙️ Instalación

### 1. settings.py
```python
INSTALLED_APPS = [
    ...
    'apps.transportes',   # ← agregar
]
```

### 2. config/urls.py
```python
path('transportes/', include('apps.transportes.urls', namespace='transportes')),
```

### 3. Migrar
```bash
python manage.py makemigrations transportes
python manage.py migrate
```

### 4. Datos necesarios (Pillow para fotos)
```bash
pip install Pillow
```

---

## 🔗 URLs disponibles (28 rutas)

| Grupo         | Rutas                                                                    |
|---------------|--------------------------------------------------------------------------|
| Dashboard     | `/transportes/`                                                          |
| Vehículos     | lista / nuevo / detalle / editar                                         |
| Conductores   | lista / nuevo / detalle / editar                                         |
| Rutas         | lista / nueva / detalle / editar / agregar-punto / eliminar-punto        |
| Despachos     | lista / nuevo / detalle / iniciar / finalizar / cancelar / actualizar-entrega |
| Mantenimientos| lista / nuevo / completar                                                |

---

## 📊 ERP COMPLETO — TODOS LOS MÓDULOS

| # | Módulo         | Descripción                                    | Estado        |
|---|----------------|------------------------------------------------|---------------|
| 1 | `core`         | Auth JWT, usuarios, roles RBAC, auditoría      | ✅ Completado |
| 2 | `rrhh`         | Empleados, nómina, vacaciones                  | ✅ Completado |
| 3 | `compras`      | Proveedores, órdenes de compra, recepciones    | ✅ Completado |
| 4 | `ventas`       | Clientes, cotizaciones, pedidos, despachos     | ✅ Completado |
| 5 | `produccion`   | Fórmulas, órdenes, lotes, control de calidad   | ✅ Completado |
| 6 | `tesoreria`    | Bancos, cajas, CXC, CXP, transferencias        | ✅ Completado |
| 7 | `contabilidad` | Plan de cuentas, asientos, 4 reportes          | ✅ Completado |
| 8 | `transportes`  | Vehículos, conductores, rutas, despachos       | ✅ Completado |

---

## 🏁 Instalación completa del ERP

```python
# settings.py — INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'apps.core',
    'apps.rrhh',
    'apps.compras',
    'apps.ventas',
    'apps.produccion',
    'apps.tesoreria',
    'apps.contabilidad',
    'apps.transportes',
]

# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',          include('apps.core.urls',          namespace='core')),
    path('rrhh/',     include('apps.rrhh.urls',          namespace='rrhh')),
    path('compras/',  include('apps.compras.urls',        namespace='compras')),
    path('ventas/',   include('apps.ventas.urls',         namespace='ventas')),
    path('produccion/',include('apps.produccion.urls',    namespace='produccion')),
    path('tesoreria/',include('apps.tesoreria.urls',      namespace='tesoreria')),
    path('contabilidad/',include('apps.contabilidad.urls',namespace='contabilidad')),
    path('transportes/',include('apps.transportes.urls',  namespace='transportes')),
]
```

```bash
# Migrar todos los módulos
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
