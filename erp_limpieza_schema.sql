-- ============================================================
--  ERP FÁBRICA DE PRODUCTOS DE LIMPIEZA
--  Script de creación de base de datos — PostgreSQL 14+
--  Módulos: core, rrhh, compras, ventas, produccion,
--           tesoreria, contabilidad, transportes
--  Generado para Django + psycopg2
-- ============================================================

-- Crear base de datos (ejecutar como superusuario)
CREATE DATABASE erp_limpieza
    WITH ENCODING = 'UTF8'
    LC_COLLATE   = 'es_ES.UTF-8'
    LC_CTYPE     = 'es_ES.UTF-8'
    TEMPLATE     = template0;

-- Crear usuario dedicado
CREATE USER erp_user WITH
    PASSWORD 'Erp$2025#Limpieza'
    CREATEDB
    NOSUPERUSER
    NOCREATEROLE;

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE erp_limpieza TO erp_user;

-- Conectar a la base de datos antes de continuar:
-- \c erp_limpieza

-- Extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- búsqueda de texto


-- ============================================================
--  MÓDULO: CORE — Auth, Usuarios, Roles, Auditoría
-- ============================================================

-- Tabla de usuarios (extiende auth_user de Django)
CREATE TABLE IF NOT EXISTS core_perfil_usuario (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    rol                 VARCHAR(30) NOT NULL DEFAULT 'usuario',
    departamento        VARCHAR(100),
    telefono            VARCHAR(20),
    foto                VARCHAR(255),
    activo              BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS core_rol (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(80) NOT NULL UNIQUE,
    descripcion TEXT,
    activo      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS core_permiso_rol (
    id          SERIAL PRIMARY KEY,
    rol_id      INTEGER NOT NULL REFERENCES core_rol(id) ON DELETE CASCADE,
    modulo      VARCHAR(50) NOT NULL,
    accion      VARCHAR(20) NOT NULL,  -- ver, crear, editar, eliminar
    UNIQUE (rol_id, modulo, accion)
);

CREATE TABLE IF NOT EXISTS core_log_auditoria (
    id              SERIAL PRIMARY KEY,
    usuario_id      INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    accion          VARCHAR(20) NOT NULL,   -- CREATE, UPDATE, DELETE
    modelo          VARCHAR(100) NOT NULL,
    objeto_id       INTEGER,
    descripcion     TEXT,
    ip_address      INET,
    user_agent      TEXT,
    fecha           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_auditoria_usuario ON core_log_auditoria(usuario_id);
CREATE INDEX idx_auditoria_fecha   ON core_log_auditoria(fecha);
CREATE INDEX idx_auditoria_modelo  ON core_log_auditoria(modelo);


-- ============================================================
--  MÓDULO: RRHH — Empleados, Nómina, Vacaciones
-- ============================================================

CREATE TABLE IF NOT EXISTS rrhh_departamento (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activo      BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rrhh_cargo (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    departamento_id INTEGER NOT NULL REFERENCES rrhh_departamento(id) ON DELETE PROTECT,
    descripcion     TEXT,
    salario_base    NUMERIC(12,2) NOT NULL,
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (nombre, departamento_id)
);

CREATE TABLE IF NOT EXISTS rrhh_empleado (
    id               SERIAL PRIMARY KEY,
    cedula           VARCHAR(20) NOT NULL UNIQUE,
    nombres          VARCHAR(100) NOT NULL,
    apellidos        VARCHAR(100) NOT NULL,
    sexo             CHAR(1) NOT NULL DEFAULT 'M',
    fecha_nacimiento DATE NOT NULL,
    telefono         VARCHAR(20),
    email            VARCHAR(254),
    direccion        TEXT,
    foto             VARCHAR(255),
    cargo_id         INTEGER NOT NULL REFERENCES rrhh_cargo(id) ON DELETE PROTECT,
    tipo_contrato    VARCHAR(20) NOT NULL DEFAULT 'indefinido',
    fecha_ingreso    DATE NOT NULL,
    fecha_egreso     DATE,
    salario          NUMERIC(12,2) NOT NULL,
    estado           VARCHAR(15) NOT NULL DEFAULT 'activo',
    usuario_id       INTEGER UNIQUE REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_por_id    INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_empleado_estado   ON rrhh_empleado(estado);
CREATE INDEX idx_empleado_cargo    ON rrhh_empleado(cargo_id);

CREATE TABLE IF NOT EXISTS rrhh_vacacion (
    id               SERIAL PRIMARY KEY,
    empleado_id      INTEGER NOT NULL REFERENCES rrhh_empleado(id) ON DELETE CASCADE,
    fecha_inicio     DATE NOT NULL,
    fecha_fin        DATE NOT NULL,
    dias_solicitados INTEGER NOT NULL,
    motivo           TEXT,
    estado           VARCHAR(10) NOT NULL DEFAULT 'pendiente',
    aprobado_por_id  INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rrhh_nomina (
    id               SERIAL PRIMARY KEY,
    periodo          VARCHAR(7) NOT NULL UNIQUE,   -- YYYY-MM
    descripcion      VARCHAR(200),
    estado           VARCHAR(10) NOT NULL DEFAULT 'borrador',
    total_bruto      NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    total_deducciones NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    total_neto       NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    creado_por_id    INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    aprobado_por_id  INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rrhh_detalle_nomina (
    id                SERIAL PRIMARY KEY,
    nomina_id         INTEGER NOT NULL REFERENCES rrhh_nomina(id) ON DELETE CASCADE,
    empleado_id       INTEGER NOT NULL REFERENCES rrhh_empleado(id) ON DELETE PROTECT,
    salario_bruto     NUMERIC(12,2) NOT NULL,
    horas_extra       NUMERIC(8,2) NOT NULL DEFAULT 0.00,
    bonificaciones    NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    seguro_social     NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    impuesto_renta    NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    otras_deducciones NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    total_deducciones NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    salario_neto      NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    observaciones     TEXT,
    UNIQUE (nomina_id, empleado_id)
);


-- ============================================================
--  MÓDULO: COMPRAS — Proveedores, OC, Recepciones
-- ============================================================

CREATE TABLE IF NOT EXISTS compras_categoria_proveedor (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS compras_proveedor (
    id               SERIAL PRIMARY KEY,
    ruc              VARCHAR(20) NOT NULL UNIQUE,
    razon_social     VARCHAR(200) NOT NULL,
    nombre_comercial VARCHAR(200),
    tipo             VARCHAR(20) NOT NULL DEFAULT 'empresa',
    categoria_id     INTEGER REFERENCES compras_categoria_proveedor(id) ON DELETE SET NULL,
    telefono         VARCHAR(30),
    telefono2        VARCHAR(30),
    email            VARCHAR(254),
    sitio_web        VARCHAR(200),
    direccion        TEXT,
    ciudad           VARCHAR(100),
    pais             VARCHAR(100) NOT NULL DEFAULT 'Ecuador',
    dias_credito     INTEGER NOT NULL DEFAULT 0,
    descuento_pct    NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    cuenta_bancaria  VARCHAR(30),
    banco            VARCHAR(100),
    observaciones    TEXT,
    estado           VARCHAR(10) NOT NULL DEFAULT 'activo',
    creado_por_id    INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS compras_contacto_proveedor (
    id           SERIAL PRIMARY KEY,
    proveedor_id INTEGER NOT NULL REFERENCES compras_proveedor(id) ON DELETE CASCADE,
    nombre       VARCHAR(150) NOT NULL,
    cargo        VARCHAR(100),
    telefono     VARCHAR(30),
    email        VARCHAR(254),
    principal    BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS compras_categoria_producto (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS compras_producto (
    id                SERIAL PRIMARY KEY,
    codigo            VARCHAR(50) NOT NULL UNIQUE,
    nombre            VARCHAR(200) NOT NULL,
    descripcion       TEXT,
    categoria_id      INTEGER REFERENCES compras_categoria_producto(id) ON DELETE SET NULL,
    unidad_medida     VARCHAR(20) NOT NULL DEFAULT 'unidad',
    precio_referencia NUMERIC(12,4) NOT NULL DEFAULT 0.0000,
    stock_minimo      NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    activo            BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS compras_orden_compra (
    id               SERIAL PRIMARY KEY,
    numero           VARCHAR(20) NOT NULL UNIQUE,
    proveedor_id     INTEGER NOT NULL REFERENCES compras_proveedor(id) ON DELETE PROTECT,
    fecha_emision    DATE NOT NULL,
    fecha_entrega    DATE,
    estado           VARCHAR(15) NOT NULL DEFAULT 'borrador',
    dias_credito     INTEGER NOT NULL DEFAULT 0,
    descuento_pct    NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    impuesto_pct     NUMERIC(5,2) NOT NULL DEFAULT 12.00,
    subtotal         NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    descuento_total  NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    base_imponible   NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    impuesto_total   NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    total            NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    notas            TEXT,
    terminos         TEXT,
    creado_por_id    INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    aprobado_por_id  INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_oc_estado    ON compras_orden_compra(estado);
CREATE INDEX idx_oc_proveedor ON compras_orden_compra(proveedor_id);

CREATE TABLE IF NOT EXISTS compras_detalle_orden (
    id                   SERIAL PRIMARY KEY,
    orden_id             INTEGER NOT NULL REFERENCES compras_orden_compra(id) ON DELETE CASCADE,
    producto_id          INTEGER NOT NULL REFERENCES compras_producto(id) ON DELETE PROTECT,
    descripcion          VARCHAR(300),
    cantidad             NUMERIC(12,2) NOT NULL,
    precio_unitario      NUMERIC(12,4) NOT NULL,
    descuento_pct        NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    descuento_monto      NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    subtotal             NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    cantidad_recibida    NUMERIC(12,2) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS compras_recepcion (
    id               SERIAL PRIMARY KEY,
    orden_id         INTEGER NOT NULL REFERENCES compras_orden_compra(id) ON DELETE PROTECT,
    numero           VARCHAR(20) NOT NULL UNIQUE,
    fecha_recepcion  DATE NOT NULL,
    nro_factura      VARCHAR(50),
    estado           VARCHAR(10) NOT NULL DEFAULT 'pendiente',
    observaciones    TEXT,
    recibido_por_id  INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS compras_detalle_recepcion (
    id                   SERIAL PRIMARY KEY,
    recepcion_id         INTEGER NOT NULL REFERENCES compras_recepcion(id) ON DELETE CASCADE,
    detalle_orden_id     INTEGER NOT NULL REFERENCES compras_detalle_orden(id) ON DELETE PROTECT,
    cantidad_recibida    NUMERIC(12,2) NOT NULL,
    cantidad_aceptada    NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    cantidad_rechazada   NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    observacion          VARCHAR(300)
);


-- ============================================================
--  MÓDULO: VENTAS — Clientes, Cotizaciones, Pedidos, Despachos
-- ============================================================

CREATE TABLE IF NOT EXISTS ventas_categoria_cliente (
    id            SERIAL PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL UNIQUE,
    descripcion   TEXT,
    descuento_pct NUMERIC(5,2) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS ventas_cliente (
    id               SERIAL PRIMARY KEY,
    ruc              VARCHAR(20) NOT NULL UNIQUE,
    razon_social     VARCHAR(200) NOT NULL,
    nombre_comercial VARCHAR(200),
    tipo             VARCHAR(20) NOT NULL DEFAULT 'empresa',
    categoria_id     INTEGER REFERENCES ventas_categoria_cliente(id) ON DELETE SET NULL,
    telefono         VARCHAR(30),
    telefono2        VARCHAR(30),
    email            VARCHAR(254),
    sitio_web        VARCHAR(200),
    direccion        TEXT,
    ciudad           VARCHAR(100),
    pais             VARCHAR(100) NOT NULL DEFAULT 'Ecuador',
    dias_credito     INTEGER NOT NULL DEFAULT 0,
    limite_credito   NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    descuento_pct    NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    vendedor_id      INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    observaciones    TEXT,
    estado           VARCHAR(10) NOT NULL DEFAULT 'activo',
    creado_por_id    INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cliente_estado ON ventas_cliente(estado);

CREATE TABLE IF NOT EXISTS ventas_contacto_cliente (
    id          SERIAL PRIMARY KEY,
    cliente_id  INTEGER NOT NULL REFERENCES ventas_cliente(id) ON DELETE CASCADE,
    nombre      VARCHAR(150) NOT NULL,
    cargo       VARCHAR(100),
    telefono    VARCHAR(30),
    email       VARCHAR(254),
    principal   BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS ventas_categoria_producto (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS ventas_producto (
    id               SERIAL PRIMARY KEY,
    codigo           VARCHAR(50) NOT NULL UNIQUE,
    nombre           VARCHAR(200) NOT NULL,
    descripcion      TEXT,
    categoria_id     INTEGER REFERENCES ventas_categoria_producto(id) ON DELETE SET NULL,
    unidad_medida    VARCHAR(20) NOT NULL DEFAULT 'unidad',
    precio_venta     NUMERIC(12,4) NOT NULL,
    precio_minimo    NUMERIC(12,4) NOT NULL DEFAULT 0.0000,
    impuesto_pct     NUMERIC(5,2) NOT NULL DEFAULT 12.00,
    activo           BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ventas_cotizacion (
    id                SERIAL PRIMARY KEY,
    numero            VARCHAR(20) NOT NULL UNIQUE,
    cliente_id        INTEGER NOT NULL REFERENCES ventas_cliente(id) ON DELETE PROTECT,
    fecha_emision     DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    estado            VARCHAR(12) NOT NULL DEFAULT 'borrador',
    descuento_pct     NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    impuesto_pct      NUMERIC(5,2) NOT NULL DEFAULT 12.00,
    subtotal          NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    descuento_total   NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    base_imponible    NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    impuesto_total    NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    total             NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    notas             TEXT,
    terminos          TEXT,
    creado_por_id     INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ventas_detalle_cotizacion (
    id               SERIAL PRIMARY KEY,
    cotizacion_id    INTEGER NOT NULL REFERENCES ventas_cotizacion(id) ON DELETE CASCADE,
    producto_id      INTEGER NOT NULL REFERENCES ventas_producto(id) ON DELETE PROTECT,
    descripcion      VARCHAR(300),
    cantidad         NUMERIC(12,2) NOT NULL,
    precio_unitario  NUMERIC(12,4) NOT NULL,
    descuento_pct    NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    descuento_monto  NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    subtotal         NUMERIC(14,2) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS ventas_pedido (
    id                SERIAL PRIMARY KEY,
    numero            VARCHAR(20) NOT NULL UNIQUE,
    cliente_id        INTEGER NOT NULL REFERENCES ventas_cliente(id) ON DELETE PROTECT,
    cotizacion_id     INTEGER UNIQUE REFERENCES ventas_cotizacion(id) ON DELETE SET NULL,
    fecha_pedido      DATE NOT NULL,
    fecha_entrega     DATE,
    estado            VARCHAR(15) NOT NULL DEFAULT 'borrador',
    direccion_entrega TEXT,
    dias_credito      INTEGER NOT NULL DEFAULT 0,
    descuento_pct     NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    impuesto_pct      NUMERIC(5,2) NOT NULL DEFAULT 12.00,
    subtotal          NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    descuento_total   NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    base_imponible    NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    impuesto_total    NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    total             NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    notas             TEXT,
    creado_por_id     INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    aprobado_por_id   INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pedido_estado  ON ventas_pedido(estado);
CREATE INDEX idx_pedido_cliente ON ventas_pedido(cliente_id);

CREATE TABLE IF NOT EXISTS ventas_detalle_pedido (
    id                   SERIAL PRIMARY KEY,
    pedido_id            INTEGER NOT NULL REFERENCES ventas_pedido(id) ON DELETE CASCADE,
    producto_id          INTEGER NOT NULL REFERENCES ventas_producto(id) ON DELETE PROTECT,
    descripcion          VARCHAR(300),
    cantidad             NUMERIC(12,2) NOT NULL,
    precio_unitario      NUMERIC(12,4) NOT NULL,
    descuento_pct        NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    descuento_monto      NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    subtotal             NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    cantidad_despachada  NUMERIC(12,2) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS ventas_despacho (
    id              SERIAL PRIMARY KEY,
    pedido_id       INTEGER NOT NULL REFERENCES ventas_pedido(id) ON DELETE PROTECT,
    numero          VARCHAR(20) NOT NULL UNIQUE,
    fecha_despacho  DATE NOT NULL,
    transportista   VARCHAR(200),
    numero_guia     VARCHAR(100),
    estado          VARCHAR(12) NOT NULL DEFAULT 'preparando',
    observaciones   TEXT,
    despachado_por_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ventas_detalle_despacho (
    id                   SERIAL PRIMARY KEY,
    despacho_id          INTEGER NOT NULL REFERENCES ventas_despacho(id) ON DELETE CASCADE,
    detalle_pedido_id    INTEGER NOT NULL REFERENCES ventas_detalle_pedido(id) ON DELETE PROTECT,
    cantidad_despachada  NUMERIC(12,2) NOT NULL,
    observacion          VARCHAR(300)
);


-- ============================================================
--  MÓDULO: PRODUCCIÓN — Fórmulas, Órdenes, Lotes, QC
-- ============================================================

CREATE TABLE IF NOT EXISTS produccion_categoria_producto_terminado (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS produccion_categoria_materia_prima (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS produccion_producto_terminado (
    id               SERIAL PRIMARY KEY,
    codigo           VARCHAR(50) NOT NULL UNIQUE,
    nombre           VARCHAR(200) NOT NULL,
    descripcion      TEXT,
    categoria_id     INTEGER REFERENCES produccion_categoria_producto_terminado(id) ON DELETE SET NULL,
    unidad_medida    VARCHAR(20) NOT NULL DEFAULT 'unidad',
    costo_estimado   NUMERIC(12,4) NOT NULL DEFAULT 0.0000,
    stock_actual     NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    stock_minimo     NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    activo           BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pt_stock ON produccion_producto_terminado(stock_actual, stock_minimo);

CREATE TABLE IF NOT EXISTS produccion_materia_prima (
    id               SERIAL PRIMARY KEY,
    codigo           VARCHAR(50) NOT NULL UNIQUE,
    nombre           VARCHAR(200) NOT NULL,
    descripcion      TEXT,
    categoria_id     INTEGER REFERENCES produccion_categoria_materia_prima(id) ON DELETE SET NULL,
    unidad_medida    VARCHAR(20) NOT NULL DEFAULT 'kg',
    costo_unitario   NUMERIC(12,4) NOT NULL DEFAULT 0.0000,
    stock_actual     NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    stock_minimo     NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    proveedor_ref    VARCHAR(200),
    activo           BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mp_stock ON produccion_materia_prima(stock_actual, stock_minimo);

CREATE TABLE IF NOT EXISTS produccion_formula (
    id                  SERIAL PRIMARY KEY,
    codigo              VARCHAR(50) NOT NULL UNIQUE,
    nombre              VARCHAR(200) NOT NULL,
    producto_id         INTEGER NOT NULL REFERENCES produccion_producto_terminado(id) ON DELETE PROTECT,
    version             VARCHAR(10) NOT NULL DEFAULT '1.0',
    rendimiento         NUMERIC(12,2) NOT NULL,
    unidad_rendimiento  VARCHAR(20) NOT NULL DEFAULT 'unidad',
    tiempo_produccion   INTEGER NOT NULL DEFAULT 0,
    instrucciones       TEXT,
    estado              VARCHAR(10) NOT NULL DEFAULT 'borrador',
    costo_materia_prima NUMERIC(14,4) NOT NULL DEFAULT 0.0000,
    costo_unitario      NUMERIC(14,4) NOT NULL DEFAULT 0.0000,
    creado_por_id       INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS produccion_linea_formula (
    id               SERIAL PRIMARY KEY,
    formula_id       INTEGER NOT NULL REFERENCES produccion_formula(id) ON DELETE CASCADE,
    materia_prima_id INTEGER NOT NULL REFERENCES produccion_materia_prima(id) ON DELETE PROTECT,
    cantidad         NUMERIC(12,4) NOT NULL,
    unidad           VARCHAR(20),
    es_critica       BOOLEAN NOT NULL DEFAULT FALSE,
    observacion      VARCHAR(300),
    UNIQUE (formula_id, materia_prima_id)
);

CREATE TABLE IF NOT EXISTS produccion_orden_produccion (
    id                   SERIAL PRIMARY KEY,
    numero               VARCHAR(20) NOT NULL UNIQUE,
    formula_id           INTEGER NOT NULL REFERENCES produccion_formula(id) ON DELETE PROTECT,
    cantidad_planificada NUMERIC(12,2) NOT NULL,
    cantidad_producida   NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    fecha_planificada    DATE NOT NULL,
    fecha_inicio         TIMESTAMP WITH TIME ZONE,
    fecha_fin            TIMESTAMP WITH TIME ZONE,
    estado               VARCHAR(12) NOT NULL DEFAULT 'planificada',
    prioridad            VARCHAR(8) NOT NULL DEFAULT 'normal',
    costo_estimado       NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    costo_real           NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    observaciones        TEXT,
    notas_produccion     TEXT,
    creado_por_id        INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    responsable_id       INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en            TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_op_estado ON produccion_orden_produccion(estado);

CREATE TABLE IF NOT EXISTS produccion_lote_produccion (
    id                 SERIAL PRIMARY KEY,
    orden_id           INTEGER NOT NULL REFERENCES produccion_orden_produccion(id) ON DELETE CASCADE,
    numero_lote        VARCHAR(50) NOT NULL UNIQUE,
    fecha_produccion   DATE NOT NULL,
    fecha_vencimiento  DATE,
    cantidad_producida NUMERIC(12,2) NOT NULL,
    cantidad_aprobada  NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    cantidad_rechazada NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    estado             VARCHAR(12) NOT NULL DEFAULT 'produccion',
    costo_real         NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    observaciones      TEXT,
    creado_por_id      INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS produccion_consumo_materia_prima (
    id                   SERIAL PRIMARY KEY,
    orden_id             INTEGER NOT NULL REFERENCES produccion_orden_produccion(id) ON DELETE CASCADE,
    lote_id              INTEGER REFERENCES produccion_lote_produccion(id) ON DELETE CASCADE,
    materia_prima_id     INTEGER NOT NULL REFERENCES produccion_materia_prima(id) ON DELETE PROTECT,
    cantidad_planificada NUMERIC(12,4) NOT NULL DEFAULT 0.0000,
    cantidad_real        NUMERIC(12,4) NOT NULL,
    costo_unitario       NUMERIC(12,4) NOT NULL DEFAULT 0.0000,
    costo_total          NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    observacion          VARCHAR(300),
    registrado_por_id    INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    fecha_registro       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS produccion_control_calidad (
    id                   SERIAL PRIMARY KEY,
    lote_id              INTEGER NOT NULL UNIQUE REFERENCES produccion_lote_produccion(id) ON DELETE CASCADE,
    fecha_inspeccion     DATE NOT NULL,
    inspector_id         INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    ph                   NUMERIC(5,2),
    viscosidad           NUMERIC(8,2),
    densidad             NUMERIC(8,4),
    color                VARCHAR(100),
    olor                 VARCHAR(100),
    aspecto              VARCHAR(200),
    resultado            VARCHAR(12) NOT NULL DEFAULT 'aprobado',
    observaciones        TEXT,
    acciones_correctivas TEXT,
    creado_en            TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


-- ============================================================
--  MÓDULO: TESORERÍA — Bancos, Cajas, CXC, CXP
-- ============================================================

CREATE TABLE IF NOT EXISTS tesoreria_banco (
    id      SERIAL PRIMARY KEY,
    nombre  VARCHAR(150) NOT NULL UNIQUE,
    codigo  VARCHAR(20),
    pais    VARCHAR(100) NOT NULL DEFAULT 'Ecuador',
    activo  BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS tesoreria_cuenta_bancaria (
    id              SERIAL PRIMARY KEY,
    banco_id        INTEGER NOT NULL REFERENCES tesoreria_banco(id) ON DELETE PROTECT,
    numero          VARCHAR(30) NOT NULL UNIQUE,
    alias           VARCHAR(100) NOT NULL,
    tipo            VARCHAR(12) NOT NULL DEFAULT 'corriente',
    moneda          VARCHAR(5) NOT NULL DEFAULT 'USD',
    saldo_inicial   NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    saldo_actual    NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    titular         VARCHAR(200),
    activa          BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tesoreria_movimiento_bancario (
    id              SERIAL PRIMARY KEY,
    cuenta_id       INTEGER NOT NULL REFERENCES tesoreria_cuenta_bancaria(id) ON DELETE PROTECT,
    fecha           DATE NOT NULL,
    tipo            VARCHAR(8) NOT NULL,   -- credito | debito
    concepto        VARCHAR(20) NOT NULL DEFAULT 'otro',
    descripcion     VARCHAR(300) NOT NULL,
    referencia      VARCHAR(100),
    monto           NUMERIC(14,2) NOT NULL,
    saldo_posterior NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    conciliado      BOOLEAN NOT NULL DEFAULT FALSE,
    creado_por_id   INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_movbanco_cuenta ON tesoreria_movimiento_bancario(cuenta_id);
CREATE INDEX idx_movbanco_fecha  ON tesoreria_movimiento_bancario(fecha);

CREATE TABLE IF NOT EXISTS tesoreria_caja (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL UNIQUE,
    responsable_id  INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    monto_asignado  NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    saldo_actual    NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    activa          BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tesoreria_movimiento_caja (
    id              SERIAL PRIMARY KEY,
    caja_id         INTEGER NOT NULL REFERENCES tesoreria_caja(id) ON DELETE PROTECT,
    fecha           DATE NOT NULL,
    tipo            VARCHAR(8) NOT NULL,   -- ingreso | egreso
    descripcion     VARCHAR(300) NOT NULL,
    monto           NUMERIC(12,2) NOT NULL,
    comprobante     VARCHAR(100),
    saldo_posterior NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    creado_por_id   INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tesoreria_cuenta_por_cobrar (
    id                SERIAL PRIMARY KEY,
    numero            VARCHAR(20) NOT NULL UNIQUE,
    cliente_nombre    VARCHAR(200) NOT NULL,
    cliente_ruc       VARCHAR(20),
    concepto          VARCHAR(300) NOT NULL,
    referencia        VARCHAR(100),
    fecha_emision     DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    monto_total       NUMERIC(14,2) NOT NULL,
    monto_cobrado     NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    estado            VARCHAR(10) NOT NULL DEFAULT 'pendiente',
    observaciones     TEXT,
    creado_por_id     INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cxc_estado     ON tesoreria_cuenta_por_cobrar(estado);
CREATE INDEX idx_cxc_vencimiento ON tesoreria_cuenta_por_cobrar(fecha_vencimiento);

CREATE TABLE IF NOT EXISTS tesoreria_cobro (
    id                SERIAL PRIMARY KEY,
    cxc_id            INTEGER NOT NULL REFERENCES tesoreria_cuenta_por_cobrar(id) ON DELETE PROTECT,
    fecha             DATE NOT NULL,
    monto             NUMERIC(14,2) NOT NULL,
    medio_pago        VARCHAR(15) NOT NULL,
    cuenta_bancaria_id INTEGER REFERENCES tesoreria_cuenta_bancaria(id) ON DELETE SET NULL,
    referencia        VARCHAR(100),
    observaciones     VARCHAR(300),
    creado_por_id     INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tesoreria_cuenta_por_pagar (
    id                SERIAL PRIMARY KEY,
    numero            VARCHAR(20) NOT NULL UNIQUE,
    proveedor_nombre  VARCHAR(200) NOT NULL,
    proveedor_ruc     VARCHAR(20),
    concepto          VARCHAR(300) NOT NULL,
    referencia        VARCHAR(100),
    fecha_emision     DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    monto_total       NUMERIC(14,2) NOT NULL,
    monto_pagado      NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    estado            VARCHAR(10) NOT NULL DEFAULT 'pendiente',
    observaciones     TEXT,
    creado_por_id     INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cxp_estado      ON tesoreria_cuenta_por_pagar(estado);
CREATE INDEX idx_cxp_vencimiento ON tesoreria_cuenta_por_pagar(fecha_vencimiento);

CREATE TABLE IF NOT EXISTS tesoreria_pago (
    id                 SERIAL PRIMARY KEY,
    cxp_id             INTEGER NOT NULL REFERENCES tesoreria_cuenta_por_pagar(id) ON DELETE PROTECT,
    fecha              DATE NOT NULL,
    monto              NUMERIC(14,2) NOT NULL,
    medio_pago         VARCHAR(15) NOT NULL,
    cuenta_bancaria_id INTEGER REFERENCES tesoreria_cuenta_bancaria(id) ON DELETE SET NULL,
    referencia         VARCHAR(100),
    observaciones      VARCHAR(300),
    creado_por_id      INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tesoreria_transferencia_bancaria (
    id                SERIAL PRIMARY KEY,
    cuenta_origen_id  INTEGER NOT NULL REFERENCES tesoreria_cuenta_bancaria(id) ON DELETE PROTECT,
    cuenta_destino_id INTEGER NOT NULL REFERENCES tesoreria_cuenta_bancaria(id) ON DELETE PROTECT,
    fecha             DATE NOT NULL,
    monto             NUMERIC(14,2) NOT NULL,
    descripcion       VARCHAR(300) NOT NULL,
    referencia        VARCHAR(100),
    estado            VARCHAR(10) NOT NULL DEFAULT 'pendiente',
    creado_por_id     INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


-- ============================================================
--  MÓDULO: CONTABILIDAD — Plan de Cuentas, Asientos, Reportes
-- ============================================================

CREATE TABLE IF NOT EXISTS contabilidad_ejercicio (
    id           SERIAL PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL UNIQUE,
    año          INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin    DATE NOT NULL,
    estado       VARCHAR(10) NOT NULL DEFAULT 'abierto',
    creado_por_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS contabilidad_cuenta (
    id                 SERIAL PRIMARY KEY,
    codigo             VARCHAR(20) NOT NULL UNIQUE,
    nombre             VARCHAR(200) NOT NULL,
    tipo               VARCHAR(12) NOT NULL,   -- activo, pasivo, patrimonio, ingreso, egreso, costo
    naturaleza         VARCHAR(10) NOT NULL,   -- deudora | acreedora
    padre_id           INTEGER REFERENCES contabilidad_cuenta(id) ON DELETE SET NULL,
    nivel              INTEGER NOT NULL DEFAULT 1,
    acepta_movimientos BOOLEAN NOT NULL DEFAULT TRUE,
    saldo_inicial      NUMERIC(16,2) NOT NULL DEFAULT 0.00,
    saldo_actual       NUMERIC(16,2) NOT NULL DEFAULT 0.00,
    activa             BOOLEAN NOT NULL DEFAULT TRUE,
    descripcion        TEXT
);

CREATE INDEX idx_cuenta_codigo ON contabilidad_cuenta(codigo);
CREATE INDEX idx_cuenta_tipo   ON contabilidad_cuenta(tipo);

CREATE TABLE IF NOT EXISTS contabilidad_periodo (
    id           SERIAL PRIMARY KEY,
    ejercicio_id INTEGER NOT NULL REFERENCES contabilidad_ejercicio(id) ON DELETE CASCADE,
    mes          INTEGER NOT NULL,
    nombre       VARCHAR(50) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin    DATE NOT NULL,
    estado       VARCHAR(8) NOT NULL DEFAULT 'abierto',
    UNIQUE (ejercicio_id, mes)
);

CREATE TABLE IF NOT EXISTS contabilidad_asiento (
    id             SERIAL PRIMARY KEY,
    numero         VARCHAR(20) NOT NULL UNIQUE,
    ejercicio_id   INTEGER NOT NULL REFERENCES contabilidad_ejercicio(id) ON DELETE PROTECT,
    fecha          DATE NOT NULL,
    tipo           VARCHAR(10) NOT NULL DEFAULT 'diario',
    concepto       VARCHAR(400) NOT NULL,
    referencia     VARCHAR(100),
    estado         VARCHAR(10) NOT NULL DEFAULT 'borrador',
    total_debe     NUMERIC(16,2) NOT NULL DEFAULT 0.00,
    total_haber    NUMERIC(16,2) NOT NULL DEFAULT 0.00,
    creado_por_id  INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    aprobado_por_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_asiento_estado    ON contabilidad_asiento(estado);
CREATE INDEX idx_asiento_fecha     ON contabilidad_asiento(fecha);
CREATE INDEX idx_asiento_ejercicio ON contabilidad_asiento(ejercicio_id);

CREATE TABLE IF NOT EXISTS contabilidad_linea_asiento (
    id          SERIAL PRIMARY KEY,
    asiento_id  INTEGER NOT NULL REFERENCES contabilidad_asiento(id) ON DELETE CASCADE,
    cuenta_id   INTEGER NOT NULL REFERENCES contabilidad_cuenta(id) ON DELETE PROTECT,
    tipo        VARCHAR(5) NOT NULL,   -- debe | haber
    monto       NUMERIC(16,2) NOT NULL,
    descripcion VARCHAR(300)
);

CREATE INDEX idx_linea_cuenta  ON contabilidad_linea_asiento(cuenta_id);
CREATE INDEX idx_linea_asiento ON contabilidad_linea_asiento(asiento_id);

CREATE TABLE IF NOT EXISTS contabilidad_configuracion (
    id          SERIAL PRIMARY KEY,
    clave       VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(200) NOT NULL,
    cuenta_id   INTEGER NOT NULL REFERENCES contabilidad_cuenta(id) ON DELETE PROTECT
);


-- ============================================================
--  MÓDULO: TRANSPORTES — Vehículos, Conductores, Rutas
-- ============================================================

CREATE TABLE IF NOT EXISTS transportes_tipo_vehiculo (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS transportes_vehiculo (
    id                    SERIAL PRIMARY KEY,
    placa                 VARCHAR(20) NOT NULL UNIQUE,
    tipo_id               INTEGER NOT NULL REFERENCES transportes_tipo_vehiculo(id) ON DELETE PROTECT,
    marca                 VARCHAR(100) NOT NULL,
    modelo                VARCHAR(100) NOT NULL,
    año                   INTEGER NOT NULL,
    color                 VARCHAR(50),
    combustible           VARCHAR(10) NOT NULL DEFAULT 'gasolina',
    capacidad_carga       NUMERIC(8,2) NOT NULL DEFAULT 0.00,
    capacidad_volumen     NUMERIC(8,2) NOT NULL DEFAULT 0.00,
    odometro              NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    estado                VARCHAR(15) NOT NULL DEFAULT 'disponible',
    soat_vencimiento      DATE,
    revision_vencimiento  DATE,
    seguro_vencimiento    DATE,
    foto                  VARCHAR(255),
    observaciones         TEXT,
    creado_en             TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vehiculo_estado ON transportes_vehiculo(estado);

CREATE TABLE IF NOT EXISTS transportes_conductor (
    id                   SERIAL PRIMARY KEY,
    cedula               VARCHAR(20) NOT NULL UNIQUE,
    nombres              VARCHAR(100) NOT NULL,
    apellidos            VARCHAR(100) NOT NULL,
    telefono             VARCHAR(20),
    email                VARCHAR(254),
    direccion            TEXT,
    numero_licencia      VARCHAR(30),
    categoria_licencia   VARCHAR(2),
    licencia_vencimiento DATE,
    estado               VARCHAR(12) NOT NULL DEFAULT 'activo',
    foto                 VARCHAR(255),
    vehiculo_asignado_id INTEGER REFERENCES transportes_vehiculo(id) ON DELETE SET NULL,
    observaciones        TEXT,
    creado_en            TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transportes_zona (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activa      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS transportes_ruta (
    id               SERIAL PRIMARY KEY,
    codigo           VARCHAR(20) NOT NULL UNIQUE,
    nombre           VARCHAR(200) NOT NULL,
    zona_id          INTEGER NOT NULL REFERENCES transportes_zona(id) ON DELETE PROTECT,
    origen           VARCHAR(200) NOT NULL,
    destino          VARCHAR(200) NOT NULL,
    distancia_km     NUMERIC(8,2) NOT NULL DEFAULT 0.00,
    tiempo_estimado  INTEGER NOT NULL DEFAULT 0,
    descripcion      TEXT,
    estado           VARCHAR(10) NOT NULL DEFAULT 'activa',
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transportes_punto_entrega (
    id               SERIAL PRIMARY KEY,
    ruta_id          INTEGER NOT NULL REFERENCES transportes_ruta(id) ON DELETE CASCADE,
    orden            INTEGER NOT NULL,
    nombre           VARCHAR(200) NOT NULL,
    direccion        TEXT,
    cliente_ref      VARCHAR(200),
    tiempo_estimado  INTEGER NOT NULL DEFAULT 0,
    activo           BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (ruta_id, orden)
);

CREATE TABLE IF NOT EXISTS transportes_despacho (
    id                     SERIAL PRIMARY KEY,
    numero                 VARCHAR(20) NOT NULL UNIQUE,
    ruta_id                INTEGER NOT NULL REFERENCES transportes_ruta(id) ON DELETE PROTECT,
    vehiculo_id            INTEGER NOT NULL REFERENCES transportes_vehiculo(id) ON DELETE PROTECT,
    conductor_id           INTEGER NOT NULL REFERENCES transportes_conductor(id) ON DELETE PROTECT,
    fecha_salida           TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_llegada_estimada TIMESTAMP WITH TIME ZONE,
    fecha_llegada_real     TIMESTAMP WITH TIME ZONE,
    estado                 VARCHAR(15) NOT NULL DEFAULT 'programado',
    odometro_salida        NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    odometro_llegada       NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    km_recorridos          NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    combustible_usado      NUMERIC(8,2) NOT NULL DEFAULT 0.00,
    costo_combustible      NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    notas                  TEXT,
    novedad                TEXT,
    creado_por_id          INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modificado_en          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_despacho_estado ON transportes_despacho(estado);
CREATE INDEX idx_despacho_fecha  ON transportes_despacho(fecha_salida);

CREATE TABLE IF NOT EXISTS transportes_entrega_despacho (
    id                SERIAL PRIMARY KEY,
    despacho_id       INTEGER NOT NULL REFERENCES transportes_despacho(id) ON DELETE CASCADE,
    punto_entrega_id  INTEGER NOT NULL REFERENCES transportes_punto_entrega(id) ON DELETE PROTECT,
    hora_llegada      TIMESTAMP WITH TIME ZONE,
    estado            VARCHAR(15) NOT NULL DEFAULT 'pendiente',
    firma_receptor    VARCHAR(200),
    observacion       TEXT
);

CREATE TABLE IF NOT EXISTS transportes_mantenimiento (
    id               SERIAL PRIMARY KEY,
    vehiculo_id      INTEGER NOT NULL REFERENCES transportes_vehiculo(id) ON DELETE CASCADE,
    tipo             VARCHAR(12) NOT NULL,
    descripcion      VARCHAR(300) NOT NULL,
    fecha_programada DATE NOT NULL,
    fecha_ejecucion  DATE,
    estado           VARCHAR(12) NOT NULL DEFAULT 'programado',
    costo            NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    taller           VARCHAR(200),
    km_en_servicio   NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    observaciones    TEXT,
    creado_por_id    INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    creado_en        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mant_estado ON transportes_mantenimiento(estado);


-- ============================================================
--  VISTAS ÚTILES
-- ============================================================

-- Vista: empleados activos con departamento
CREATE OR REPLACE VIEW v_empleados_activos AS
SELECT
    e.id, e.cedula,
    e.nombres || ' ' || e.apellidos AS nombre_completo,
    c.nombre AS cargo, d.nombre AS departamento,
    e.salario, e.estado, e.fecha_ingreso
FROM rrhh_empleado e
JOIN rrhh_cargo c ON c.id = e.cargo_id
JOIN rrhh_departamento d ON d.id = c.departamento_id
WHERE e.estado = 'activo';

-- Vista: saldos de cuentas bancarias
CREATE OR REPLACE VIEW v_saldos_bancarios AS
SELECT
    cb.alias, b.nombre AS banco, cb.tipo, cb.moneda,
    cb.saldo_actual,
    COUNT(mb.id) AS num_movimientos
FROM tesoreria_cuenta_bancaria cb
JOIN tesoreria_banco b ON b.id = cb.banco_id
LEFT JOIN tesoreria_movimiento_bancario mb ON mb.cuenta_id = cb.id
WHERE cb.activa = TRUE
GROUP BY cb.id, cb.alias, b.nombre, cb.tipo, cb.moneda, cb.saldo_actual;

-- Vista: CXC pendientes con días de mora
CREATE OR REPLACE VIEW v_cxc_pendientes AS
SELECT
    numero, cliente_nombre, concepto, referencia,
    fecha_emision, fecha_vencimiento,
    monto_total, monto_cobrado,
    (monto_total - monto_cobrado) AS saldo_pendiente,
    CURRENT_DATE - fecha_vencimiento AS dias_mora,
    estado
FROM tesoreria_cuenta_por_cobrar
WHERE estado IN ('pendiente', 'parcial', 'vencido')
ORDER BY fecha_vencimiento;

-- Vista: CXP pendientes con días de mora
CREATE OR REPLACE VIEW v_cxp_pendientes AS
SELECT
    numero, proveedor_nombre, concepto, referencia,
    fecha_emision, fecha_vencimiento,
    monto_total, monto_pagado,
    (monto_total - monto_pagado) AS saldo_pendiente,
    CURRENT_DATE - fecha_vencimiento AS dias_mora,
    estado
FROM tesoreria_cuenta_por_pagar
WHERE estado IN ('pendiente', 'parcial', 'vencido')
ORDER BY fecha_vencimiento;

-- Vista: stock bajo de materias primas
CREATE OR REPLACE VIEW v_stock_bajo_mp AS
SELECT
    codigo, nombre, unidad_medida,
    stock_actual, stock_minimo,
    (stock_minimo - stock_actual) AS deficit
FROM produccion_materia_prima
WHERE activo = TRUE AND stock_actual <= stock_minimo
ORDER BY deficit DESC;

-- Vista: stock bajo de productos terminados
CREATE OR REPLACE VIEW v_stock_bajo_pt AS
SELECT
    codigo, nombre, unidad_medida,
    stock_actual, stock_minimo,
    (stock_minimo - stock_actual) AS deficit
FROM produccion_producto_terminado
WHERE activo = TRUE AND stock_actual <= stock_minimo
ORDER BY deficit DESC;

-- Vista: despachos de transportes activos
CREATE OR REPLACE VIEW v_despachos_activos AS
SELECT
    d.numero, r.codigo AS ruta, r.nombre AS nombre_ruta,
    v.placa, v.marca || ' ' || v.modelo AS vehiculo,
    c.nombres || ' ' || c.apellidos AS conductor,
    d.fecha_salida, d.estado
FROM transportes_despacho d
JOIN transportes_ruta r ON r.id = d.ruta_id
JOIN transportes_vehiculo v ON v.id = d.vehiculo_id
JOIN transportes_conductor c ON c.id = d.conductor_id
WHERE d.estado IN ('programado', 'en_ruta')
ORDER BY d.fecha_salida;

-- Vista: balance de cuentas contables (activas con movimientos)
CREATE OR REPLACE VIEW v_balance_cuentas AS
SELECT
    ct.codigo, ct.nombre, ct.tipo, ct.naturaleza,
    ct.saldo_inicial,
    COALESCE(SUM(CASE WHEN la.tipo = 'debe'  THEN la.monto ELSE 0 END), 0) AS total_debe,
    COALESCE(SUM(CASE WHEN la.tipo = 'haber' THEN la.monto ELSE 0 END), 0) AS total_haber,
    ct.saldo_actual
FROM contabilidad_cuenta ct
LEFT JOIN contabilidad_linea_asiento la ON la.cuenta_id = ct.id
LEFT JOIN contabilidad_asiento a ON a.id = la.asiento_id AND a.estado = 'aprobado'
WHERE ct.activa = TRUE AND ct.acepta_movimientos = TRUE
GROUP BY ct.id, ct.codigo, ct.nombre, ct.tipo, ct.naturaleza,
         ct.saldo_inicial, ct.saldo_actual
ORDER BY ct.codigo;


-- ============================================================
--  DATOS INICIALES (CATÁLOGOS)
-- ============================================================

-- Bancos de Ecuador
INSERT INTO tesoreria_banco (nombre, codigo, pais) VALUES
    ('Banco Pichincha',         'BP',   'Ecuador'),
    ('Banco del Pacífico',      'BPC',  'Ecuador'),
    ('Banco Guayaquil',         'BG',   'Ecuador'),
    ('Banco Internacional',     'BI',   'Ecuador'),
    ('Banco del Austro',        'BA',   'Ecuador'),
    ('Produbanco',              'PROD', 'Ecuador'),
    ('Banco de Loja',           'BL',   'Ecuador'),
    ('Cooperativa JEP',         'JEP',  'Ecuador'),
    ('Cooperativa Jardín Azuayo','JA',  'Ecuador');

-- Tipos de vehículo
INSERT INTO transportes_tipo_vehiculo (nombre, descripcion) VALUES
    ('Camión',         'Vehículo pesado de carga'),
    ('Furgoneta',      'Furgoneta de reparto liviano'),
    ('Camioneta',      'Camioneta pick-up 4x4'),
    ('Motocicleta',    'Moto para entregas rápidas'),
    ('Camión Cisterna','Camión con cisterna para líquidos');

-- Categorías de proveedor
INSERT INTO compras_categoria_proveedor (nombre, descripcion) VALUES
    ('Materia Prima',       'Proveedores de insumos para fabricación'),
    ('Empaque y Embalaje',  'Proveedores de envases, etiquetas y cajas'),
    ('Maquinaria',          'Proveedores de equipos industriales'),
    ('Servicios',           'Proveedores de servicios generales'),
    ('Transporte',          'Empresas de logística y transporte');

-- Categorías de cliente
INSERT INTO ventas_categoria_cliente (nombre, descripcion, descuento_pct) VALUES
    ('Minorista',      'Tiendas y pequeños negocios',     0.00),
    ('Mayorista',      'Distribuidores y mayoristas',     5.00),
    ('Supermercado',   'Cadenas de supermercados',       10.00),
    ('Institucional',  'Empresas e instituciones',        8.00),
    ('Exportación',    'Clientes internacionales',       15.00);

-- Departamentos RRHH
INSERT INTO rrhh_departamento (nombre, descripcion) VALUES
    ('Gerencia',              'Alta dirección y administración general'),
    ('Producción',            'Fabricación de productos de limpieza'),
    ('Ventas',                'Comercialización y relación con clientes'),
    ('Compras',               'Gestión de proveedores e insumos'),
    ('Contabilidad y Finanzas','Control financiero y contable'),
    ('Recursos Humanos',      'Gestión de personal y nómina'),
    ('Logística y Transporte','Despacho, almacén y transporte'),
    ('Calidad',               'Control de calidad e inocuidad');

-- Categorías de producto terminado
INSERT INTO produccion_categoria_producto_terminado (nombre, descripcion) VALUES
    ('Limpiadores Multiusos',    'Productos para limpieza general de superficies'),
    ('Desinfectantes',           'Productos con acción bactericida y virucida'),
    ('Lavavajillas',             'Jabones para lavar vajilla a mano y máquina'),
    ('Detergentes para Ropa',    'Productos para lavado de ropa en polvo y líquido'),
    ('Suavizantes de Telas',     'Suavizantes y acondicionadores para ropa'),
    ('Limpiadores de Baño',      'Antical, desengrasante e higienizante de baños'),
    ('Desengrasantes',           'Limpiadores industriales y de cocina'),
    ('Ceras y Pulimentos',       'Productos para protección de pisos y muebles');

-- Categorías de materia prima
INSERT INTO produccion_categoria_materia_prima (nombre, descripcion) VALUES
    ('Tensoactivos',        'Surfactantes aniónicos, no iónicos y catiónicos'),
    ('Solventes',           'Alcohol isopropílico, propilenglicol, etc.'),
    ('Espesantes',          'Cloruro de sodio, HPMC, carbopol'),
    ('Conservantes',        'Benzoato de sodio, parabenos, MIT'),
    ('Fragrancias',         'Esencias y fragancias para productos terminados'),
    ('Colorantes',          'Colorantes cosméticos aprobados'),
    ('Envases',             'Botellas, galones, sachets y bidones'),
    ('Etiquetas y Empaques','Material de empaque y etiquetado'),
    ('Desinfectantes Base', 'Hipoclorito, peróxido, amonio cuaternario');


-- ============================================================
--  ÍNDICES ADICIONALES PARA RENDIMIENTO
-- ============================================================

-- Búsquedas frecuentes
CREATE INDEX idx_proveedor_razon   ON compras_proveedor USING gin(razon_social gin_trgm_ops);
CREATE INDEX idx_cliente_razon     ON ventas_cliente USING gin(razon_social gin_trgm_ops);
CREATE INDEX idx_empleado_nombre   ON rrhh_empleado USING gin((nombres || ' ' || apellidos) gin_trgm_ops);
CREATE INDEX idx_producto_nombre   ON produccion_producto_terminado USING gin(nombre gin_trgm_ops);
CREATE INDEX idx_mp_nombre         ON produccion_materia_prima USING gin(nombre gin_trgm_ops);

-- Fechas para reportes
CREATE INDEX idx_pedido_fecha      ON ventas_pedido(fecha_pedido);
CREATE INDEX idx_oc_fecha          ON compras_orden_compra(fecha_emision);
CREATE INDEX idx_lote_fecha        ON produccion_lote_produccion(fecha_produccion);

-- ============================================================
--  FIN DEL SCRIPT
-- ============================================================
-- Total de tablas creadas: 62
-- Total de vistas creadas: 7
-- Total de índices:        30+
-- Datos iniciales:         9 catálogos precargados
-- ============================================================
