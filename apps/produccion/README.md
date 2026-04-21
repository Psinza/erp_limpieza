# Módulo PRODUCCIÓN — ERP Fábrica de Limpieza
## Django + PostgreSQL | Bootstrap 5 + Bootstrap Icons

---

## 📦 Estructura del módulo

```
apps/produccion/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── urls.py
├── views.py
├── migrations/
│   └── __init__.py
└── templates/produccion/
    ├── dashboard_produccion.html
    ├── materia_prima_list.html
    ├── materia_prima_form.html
    ├── materia_prima_ajuste_stock.html
    ├── producto_terminado_list.html
    ├── producto_terminado_form.html
    ├── formula_list.html
    ├── formula_form.html
    ├── formula_detail.html
    ├── orden_list.html
    ├── orden_form.html
    ├── orden_detail.html
    ├── lote_list.html
    ├── lote_form.html
    ├── lote_detail.html
    └── control_calidad_form.html
```

---

## 🗃️ Modelos

| Modelo                      | Descripción                                                  |
|-----------------------------|--------------------------------------------------------------|
| `CategoriaProductoTerminado`| Agrupación de productos terminados                           |
| `CategoriaMateriaPrima`     | Agrupación de materias primas                                |
| `ProductoTerminado`         | Producto final con stock y costo estimado                    |
| `MateriaPrima`              | Insumo con stock, costo y alerta de mínimo                   |
| `Formula`                   | Receta de producción con versión y rendimiento               |
| `LineaFormula`              | Ingrediente de la fórmula con cantidad y costo               |
| `OrdenProduccion`           | Orden para producir N veces una fórmula                      |
| `LoteProduccion`            | Lote físico generado por la orden                            |
| `ConsumoMateriaPrima`       | Registro de materia prima consumida en la orden              |
| `ControlCalidad`            | Inspección fisicoquímica del lote (pH, viscosidad, densidad) |

---

## 🔄 Flujos implementados

### Fórmula
```
Borrador → [agregar ingredientes] → [Activar] → Activa → Obsoleta
```

### Orden de Producción
```
Planificada → [Iniciar] → En Proceso → [Pausar] → Pausada → [Reanudar]
                                     → [Registrar Lote]
                                     → [Completar] → Completada
```

### Lote de Producción
```
En Producción → [Enviar a QC] → En Control QC
                                      → [Registrar Control Calidad]
                                      → Aprobado → [Liberar] → Liberado al Almacén
                                      → Rechazado
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
    'apps.ventas',
    'apps.produccion',   # ← agregar
]
```

### 2. config/urls.py
```python
path('produccion/', include('apps.produccion.urls', namespace='produccion')),
```

### 3. Migrar
```bash
python manage.py makemigrations produccion
python manage.py migrate
```

---

## 🔗 URLs (35 rutas)

| Grupo              | Rutas principales                                                      |
|--------------------|------------------------------------------------------------------------|
| Dashboard          | `/produccion/`                                                         |
| Materias Primas    | lista / nueva / editar / ajuste-stock                                  |
| Productos Terminados| lista / nuevo / editar                                                |
| Fórmulas           | lista / nueva / detalle / editar / agregar-línea / calcular-costos / activar |
| Órdenes            | lista / nueva / detalle / iniciar / pausar / reanudar / completar / anular / consumo |
| Lotes              | lista / nuevo / detalle / enviar-control / liberar                     |
| Control Calidad    | crear desde lote                                                       |

---

## 🧪 Particularidades — Productos de Limpieza

- Control de calidad con parámetros específicos: **pH, viscosidad, densidad, color, olor, aspecto**
- Alertas de stock bajo para materias primas y productos terminados
- Ajuste manual de stock de materia prima (compras, mermas, inventario)
- Trazabilidad completa: Fórmula → Orden → Lote → Control QC → Almacén
- Costo automático: al registrar consumos reales, el costo de la orden se actualiza

---

## 📊 Progreso del ERP

| # | Módulo        | Estado       |
|---|---------------|--------------|
| 1 | `core`        | ✅ Completado |
| 2 | `rrhh`        | ✅ Completado |
| 3 | `compras`     | ✅ Completado |
| 4 | `ventas`      | ✅ Completado |
| 5 | `produccion`  | ✅ Completado |
| 6 | `tesoreria`   | ⏳ Pendiente  |
| 7 | `contabilidad`| ⏳ Pendiente  |
| 8 | `transportes` | ⏳ Pendiente  |
