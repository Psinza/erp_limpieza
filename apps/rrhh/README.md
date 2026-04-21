# Módulo RRHH — ERP Fábrica de Limpieza
## Django + PostgreSQL | Bootstrap 5 + Bootstrap Icons

---

## 📦 Contenido del módulo

```
apps/rrhh/
├── __init__.py
├── admin.py               ← Panel de administración Django
├── apps.py                ← Configuración de la app
├── forms.py               ← Formularios Bootstrap
├── models.py              ← 6 modelos de base de datos
├── urls.py                ← 22 rutas con namespace="rrhh"
├── views.py               ← Vistas CRUD + flujo de nómina
├── migrations/
│   └── __init__.py
└── templates/rrhh/
    ├── dashboard_rrhh.html
    ├── departamento_list.html
    ├── departamento_form.html
    ├── cargo_list.html
    ├── cargo_form.html
    ├── empleado_list.html
    ├── empleado_form.html
    ├── empleado_detail.html
    ├── empleado_confirm_delete.html
    ├── vacacion_list.html
    ├── vacacion_form.html
    ├── nomina_list.html
    ├── nomina_form.html
    └── nomina_detail.html
```

---

## 🗃️ Modelos

| Modelo          | Campos clave                                              |
|-----------------|-----------------------------------------------------------|
| `Departamento`  | nombre, descripcion, activo                               |
| `Cargo`         | nombre, departamento, salario_base, activo                |
| `Empleado`      | cedula, nombres, apellidos, cargo, salario, estado, foto  |
| `Vacacion`      | empleado, fecha_inicio, fecha_fin, dias, estado           |
| `Nomina`        | periodo, estado, total_bruto, total_deducciones, total_neto |
| `DetalleNomina` | nomina, empleado, salario_bruto, bonificaciones, deducciones, neto |

---

## 🔄 Flujo de Nómina

```
Borrador → [Calcular] → Calculada → [Aprobar] → Aprobada → [Pagar] → Pagada
```

---

## ⚙️ Instalación

### 1. Copiar el módulo
```
Copiar la carpeta apps/rrhh/ dentro de tu proyecto Django.
```

### 2. Registrar en settings.py
```python
INSTALLED_APPS = [
    ...
    'apps.core',
    'apps.rrhh',   # ← agregar
]
```

### 3. Registrar URLs en config/urls.py
```python
from django.urls import path, include

urlpatterns = [
    ...
    path('rrhh/', include('apps.rrhh.urls', namespace='rrhh')),
]
```

### 4. Ejecutar migraciones
```bash
python manage.py makemigrations rrhh
python manage.py migrate
```

### 5. Dependencias requeridas
```bash
pip install Pillow   # Para el campo ImageField (foto de empleado)
```

---

## 🔗 URLs disponibles

| Nombre                         | URL                                    | Método |
|--------------------------------|----------------------------------------|--------|
| `rrhh:dashboard`               | /rrhh/                                 | GET    |
| `rrhh:departamento_list`       | /rrhh/departamentos/                   | GET    |
| `rrhh:departamento_create`     | /rrhh/departamentos/nuevo/             | GET/POST|
| `rrhh:departamento_edit`       | /rrhh/departamentos/<pk>/editar/       | GET/POST|
| `rrhh:cargo_list`              | /rrhh/cargos/                          | GET    |
| `rrhh:cargo_create`            | /rrhh/cargos/nuevo/                    | GET/POST|
| `rrhh:cargo_edit`              | /rrhh/cargos/<pk>/editar/             | GET/POST|
| `rrhh:empleado_list`           | /rrhh/empleados/                       | GET    |
| `rrhh:empleado_create`         | /rrhh/empleados/nuevo/                 | GET/POST|
| `rrhh:empleado_detail`         | /rrhh/empleados/<pk>/                  | GET    |
| `rrhh:empleado_edit`           | /rrhh/empleados/<pk>/editar/           | GET/POST|
| `rrhh:empleado_delete`         | /rrhh/empleados/<pk>/baja/             | GET/POST|
| `rrhh:vacacion_list`           | /rrhh/vacaciones/                      | GET    |
| `rrhh:vacacion_create`         | /rrhh/vacaciones/nueva/                | GET/POST|
| `rrhh:vacacion_aprobar`        | /rrhh/vacaciones/<pk>/gestionar/       | POST   |
| `rrhh:nomina_list`             | /rrhh/nominas/                         | GET    |
| `rrhh:nomina_create`           | /rrhh/nominas/nueva/                   | GET/POST|
| `rrhh:nomina_detail`           | /rrhh/nominas/<pk>/                    | GET    |
| `rrhh:nomina_agregar_empleado` | /rrhh/nominas/<pk>/agregar/            | POST   |
| `rrhh:nomina_calcular`         | /rrhh/nominas/<pk>/calcular/           | GET    |
| `rrhh:nomina_aprobar`          | /rrhh/nominas/<pk>/aprobar/            | GET    |
| `rrhh:nomina_pagar`            | /rrhh/nominas/<pk>/pagar/              | GET    |

---

## 🏷️ Templates requeridos en base.html

El módulo extiende `base.html`. Asegúrate de que tu base incluya:
- Bootstrap 5 CSS y JS
- Bootstrap Icons (bi bi-*)
- Bloque `{% block content %}`
- Bloque `{% block title %}`
- Mensajes Django: `{% for message in messages %}`

---

## 📝 Próximos módulos
- `apps/compras/`   — Proveedores, Órdenes de Compra
- `apps/ventas/`    — Pedidos, Clientes
- `apps/produccion/`— Fórmulas, Lotes
- `apps/tesoreria/` — Flujo de caja, Bancos
