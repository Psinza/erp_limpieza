# ERP Industrial — Fábrica de Productos de Limpieza
> Django 4.2 · PostgreSQL · Seguridad RBAC por roles

## Módulo actual: `core` — Autenticación y Control de Acceso

---

## Instalación rápida

### 1. Clonar / descomprimir el proyecto
```bash
cd erp_limpieza
```

### 2. Crear y activar entorno virtual
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con sus datos de PostgreSQL
```

### 5. Crear base de datos en PostgreSQL
```sql
CREATE DATABASE erp_limpieza;
```

### 6. Aplicar migraciones
```bash
python manage.py makemigrations core
python manage.py migrate
```

### 7. Inicializar datos del ERP (áreas, roles, admin)
```bash
python manage.py init_erp
# Opcional: cambiar contraseña del admin
python manage.py init_erp --admin-password MiClaveSegura123
```

### 8. Ejecutar el servidor
```bash
python manage.py runserver
```

### 9. Acceder al sistema
- **ERP:** http://localhost:8000/core/login/
- **Admin Django:** http://localhost:8000/admin/
- **Usuario:** `admin` / **Contraseña:** `Admin1234!`

---

## Estructura del módulo `core`

```
apps/core/
├── models.py          # Usuario, Rol, Area, Permiso, LogAcceso
├── views.py           # Login, Dashboard, Usuarios, Roles, Perfil
├── forms.py           # LoginForm, UsuarioForm, RolForm
├── decorators.py      # @area_requerida, @permiso_requerido, @rol_requerido
├── urls.py            # Rutas del módulo
├── admin.py           # Panel de administración
├── apps.py
├── management/
│   └── commands/
│       └── init_erp.py   # Comando de inicialización
└── templates/core/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── usuario_lista.html
    ├── usuario_form.html
    ├── rol_lista.html
    ├── rol_form.html
    ├── perfil.html
    └── cambiar_password.html
```

## Roles creados automáticamente

| Rol               | Nivel          | Áreas                              |
|-------------------|----------------|------------------------------------|
| Administrador     | Superusuario   | Todas                              |
| RRHH              | L/E            | RRHH                               |
| Jefe de Compras   | Aprobador      | Compras, Almacén M.P.              |
| Jefe de Ventas    | Aprobador      | Ventas, Comercialización, Vendedores|
| Tesorero          | Aprobador      | Tesorería, Ord. Pagos              |
| Contador          | L/E            | Contabilidad                       |
| Jefe de Producción| Supervisor     | Producción, Almacenes              |
| Jefe de Logística | Supervisor     | Logística, Almacenes, Transportes  |
| Vendedor          | L/E            | Ventas, Vendedores                 |
| Transportista     | Solo lectura   | Transportes, Almacén P.T.          |

## Cómo usar los decoradores de seguridad

```python
from apps.core.decorators import area_requerida, permiso_requerido, rol_requerido

# Solo usuarios del área COMPRAS o ADMIN
@area_requerida('COMPRAS', 'ADMIN')
def mi_vista(request): ...

# Solo usuarios con permiso 'aprobar' en VENTAS
@permiso_requerido('VENTAS', 'aprobar')
def aprobar_pedido(request): ...

# Solo usuarios con el rol exacto
@rol_requerido('Tesorero', 'Administrador')
def vista_financiera(request): ...
```

## Próximos módulos

- [ ] `rrhh` — Empleados, contratos, nómina
- [ ] `compras` — Proveedores, órdenes de compra, recepciones
- [ ] `produccion` — Fórmulas, lotes, órdenes de producción
- [ ] `logistica` — Inventario, entradas/salidas, kardex
- [ ] `ventas` — Pedidos, facturas, clientes
- [ ] `tesoreria` — Caja, bancos, conciliación
- [ ] `contabilidad` — Asientos, balance, estado de resultados
- [ ] `transportes` — Vehículos, rutas, despachos
- [ ] `vendedores` — Metas, comisiones, seguimiento
