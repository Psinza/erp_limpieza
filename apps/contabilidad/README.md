# Módulo CONTABILIDAD — ERP Fábrica de Limpieza
## Django + PostgreSQL | Bootstrap 5 + Bootstrap Icons

---

## 📦 Estructura del módulo

```
apps/contabilidad/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── urls.py
├── views.py
├── migrations/
│   └── __init__.py
└── templates/contabilidad/
    ├── dashboard_contabilidad.html
    ├── ejercicio_list.html
    ├── ejercicio_form.html
    ├── plan_cuentas.html
    ├── cuenta_form.html
    ├── cuenta_mayor.html
    ├── asiento_list.html
    ├── asiento_form.html
    ├── asiento_detail.html
    ├── libro_diario.html
    ├── balance_comprobacion.html
    ├── estado_resultados.html
    ├── balance_general.html
    ├── configuracion_list.html
    └── configuracion_form.html
```

---

## 🗃️ Modelos

| Modelo                   | Descripción                                                       |
|--------------------------|-------------------------------------------------------------------|
| `EjercicioContable`      | Año fiscal con fechas de apertura y cierre                        |
| `CuentaContable`         | Plan de cuentas jerárquico por código (grupos, subgrupos, cuentas)|
| `AsientoContable`        | Comprobante contable con partida doble                            |
| `LineaAsiento`           | Línea individual de Debe/Haber ligada a una cuenta                |
| `PeriodoContable`        | Mes contable dentro de un ejercicio                               |
| `ConfiguracionContable`  | Mapeo clave→cuenta para asientos automáticos                      |

---

## 📊 Tipos de Cuenta Soportados

| Tipo          | Naturaleza  | Descripción                    |
|---------------|-------------|--------------------------------|
| `activo`      | Deudora     | Bienes y derechos de la empresa|
| `pasivo`      | Acreedora   | Obligaciones y deudas          |
| `patrimonio`  | Acreedora   | Capital y reservas             |
| `ingreso`     | Acreedora   | Ventas y otros ingresos        |
| `costo`       | Deudora     | Costo de ventas y producción   |
| `egreso`      | Deudora     | Gastos operativos              |

---

## 🔄 Flujo de Asientos Contables

```
Borrador → [Agregar líneas] → [Verificar Debe=Haber] → [Aprobar] → Aprobado
                                                                      ↓
                                                        Saldos de cuentas actualizados
              ← [Anular] (desde cualquier estado activo)
```

---

## 📋 Reportes Financieros

| Reporte                  | URL                              | Descripción                                    |
|--------------------------|----------------------------------|------------------------------------------------|
| **Libro Diario**         | `/contabilidad/libro-diario/`    | Todos los asientos aprobados por período       |
| **Balance Comprobación** | `/contabilidad/balance-comprobacion/` | Sumas y saldos de todas las cuentas       |
| **Estado de Resultados** | `/contabilidad/estado-resultados/` | Ingresos, costos, gastos y utilidad neta     |
| **Balance General**      | `/contabilidad/balance-general/` | Activos = Pasivos + Patrimonio                 |

Todos los reportes son **filtrables por ejercicio y rango de fechas**.

---

## ⚙️ Instalación

### 1. settings.py
```python
INSTALLED_APPS = [
    ...
    'apps.contabilidad',   # ← agregar
]
```

### 2. config/urls.py
```python
path('contabilidad/', include('apps.contabilidad.urls', namespace='contabilidad')),
```

### 3. Migrar
```bash
python manage.py makemigrations contabilidad
python manage.py migrate
```

### 4. Plan de cuentas inicial (recomendado)
Crea las cuentas principales usando el admin o la interfaz web.
Estructura sugerida para fábrica de limpieza:
```
1.  ACTIVOS
 1.1  Activo Corriente
  1.1.01  Caja General
  1.1.02  Bancos
  1.1.03  Cuentas por Cobrar
  1.1.04  Inventario Producto Terminado
  1.1.05  Inventario Materias Primas
 1.2  Activo No Corriente
  1.2.01  Maquinaria y Equipo
2.  PASIVOS
 2.1  Pasivo Corriente
  2.1.01  Cuentas por Pagar
  2.1.02  Nóminas por Pagar
3.  PATRIMONIO
 3.1.01  Capital Social
 3.1.02  Utilidades Retenidas
4.  INGRESOS
 4.1.01  Ventas
5.  COSTOS
 5.1.01  Costo de Ventas
6.  GASTOS
 6.1.01  Gastos Administrativos
 6.1.02  Gastos de Ventas
```

---

## 🔗 URLs disponibles (24 rutas)

| Grupo              | Rutas                                                      |
|--------------------|-------------------------------------------------------------|
| Dashboard          | `/contabilidad/`                                            |
| Ejercicios         | lista / nuevo / cerrar                                      |
| Plan de Cuentas    | lista / nueva / editar / libro mayor                        |
| Asientos           | lista / nuevo / detalle / agregar-línea / eliminar-línea / aprobar / anular |
| Reportes           | libro diario / balance comprobación / estado resultados / balance general |
| Configuración      | lista / nueva / editar                                      |

---

## 📊 Progreso del ERP

| # | Módulo        | Estado       |
|---|---------------|--------------|
| 1 | `core`        | ✅ Completado |
| 2 | `rrhh`        | ✅ Completado |
| 3 | `compras`     | ✅ Completado |
| 4 | `ventas`      | ✅ Completado |
| 5 | `produccion`  | ✅ Completado |
| 6 | `tesoreria`   | ✅ Completado |
| 7 | `contabilidad`| ✅ Completado |
| 8 | `transportes` | ⏳ Pendiente  |
