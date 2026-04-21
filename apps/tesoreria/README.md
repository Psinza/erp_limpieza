# Módulo TESORERÍA — ERP Fábrica de Limpieza
## Django + PostgreSQL | Bootstrap 5 + Bootstrap Icons

---

## 📦 Estructura del módulo

```
apps/tesoreria/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── urls.py
├── views.py
├── migrations/
│   └── __init__.py
└── templates/tesoreria/
    ├── dashboard_tesoreria.html
    ├── banco_list.html
    ├── banco_form.html
    ├── cuenta_list.html
    ├── cuenta_form.html
    ├── cuenta_detail.html
    ├── movimiento_bancario_form.html
    ├── caja_list.html
    ├── caja_form.html
    ├── caja_detail.html
    ├── movimiento_caja_form.html
    ├── cxc_list.html
    ├── cxc_form.html
    ├── cxc_detail.html
    ├── cxp_list.html
    ├── cxp_form.html
    ├── cxp_detail.html
    ├── transferencia_list.html
    ├── transferencia_form.html
    └── flujo_caja.html
```

---

## 🗃️ Modelos

| Modelo                  | Descripción                                                  |
|-------------------------|--------------------------------------------------------------|
| `Banco`                 | Catálogo de instituciones bancarias                          |
| `CuentaBancaria`        | Cuenta con saldo actualizado automáticamente                 |
| `MovimientoBancario`    | Crédito/débito con actualización de saldo en tiempo real     |
| `Caja`                  | Fondo de caja chica con responsable                          |
| `MovimientoCaja`        | Ingreso/egreso de caja con saldo actualizado                 |
| `CuentaPorCobrar`       | Documento por cobrar con seguimiento de estado               |
| `CuentaPorPagar`        | Obligación con proveedor con seguimiento de estado           |
| `Cobro`                 | Abono a una CXC (parcial o total)                            |
| `Pago`                  | Abono a una CXP (parcial o total)                            |
| `TransferenciaBancaria` | Movimiento entre cuentas propias con ejecución en dos pasos  |

---

## 🔄 Flujos implementados

### Cuentas por Cobrar
```
Nueva CXC (Pendiente) → Registrar Cobro(s) → Cobrado Parcialmente → Cobrado
                                           ← Anulado (en cualquier estado)
```

### Cuentas por Pagar
```
Nueva CXP (Pendiente) → Registrar Pago(s) → Pagado Parcialmente → Pagado
                                          ← Anulado (en cualquier estado)
```

### Transferencias
```
Nueva Transferencia (Pendiente) → [Ejecutar] → Completada
  (Al ejecutar: débita cuenta origen + acredita cuenta destino automáticamente)
```

---

## 💡 Características destacadas

- **Saldo en tiempo real**: al registrar un movimiento bancario o de caja, el saldo de la cuenta se actualiza automáticamente via `save()`
- **Cobros y pagos cruzados**: al registrar un cobro en una CXC con cuenta bancaria, se genera automáticamente el movimiento de crédito en la cuenta
- **Alertas de vencimiento**: CXC/CXP vencidas se resaltan en rojo en el dashboard y listas
- **Flujo de caja filtrable**: reporte consolidado de movimientos bancarios + caja por rango de fechas
- **Liquidez total**: suma de saldos bancarios + cajas visible en el dashboard

---

## ⚙️ Instalación

### 1. settings.py
```python
INSTALLED_APPS = [
    ...
    'apps.tesoreria',   # ← agregar
]
```

### 2. config/urls.py
```python
path('tesoreria/', include('apps.tesoreria.urls', namespace='tesoreria')),
```

### 3. Migrar
```bash
python manage.py makemigrations tesoreria
python manage.py migrate
```

---

## 🔗 URLs (30 rutas)

| Grupo              | Rutas                                                      |
|--------------------|-------------------------------------------------------------|
| Dashboard          | `/tesoreria/`                                               |
| Bancos             | lista / nuevo / editar                                      |
| Cuentas Bancarias  | lista / nueva / detalle / editar / movimiento               |
| Cajas              | lista / nueva / detalle / movimiento                        |
| CXC                | lista / nueva / detalle / registrar cobro / anular          |
| CXP                | lista / nueva / detalle / registrar pago / anular           |
| Transferencias     | lista / nueva / ejecutar                                    |
| Flujo de Caja      | reporte filtrable por período                               |

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
| 7 | `contabilidad`| ⏳ Pendiente  |
| 8 | `transportes` | ⏳ Pendiente  |
