-- ============================================================
--  ERP FÁBRICA DE PRODUCTOS DE LIMPIEZA
--  Script de creación de base de datos — Adaptado para MySQL 8.0+
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Crear base de datos
CREATE DATABASE IF NOT EXISTS erp_limpieza
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_spanish_ci;

USE erp_limpieza;

-- Nota: La tabla 'auth_user' se asume creada por el sistema de autenticación (Django).
-- Si vas a probar este script solo, crea una tabla dummy o asegúrate de que exista.

-- ============================================================
--  MÓDULO: CORE
-- ============================================================

CREATE TABLE IF NOT EXISTS core_perfil_usuario (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT NOT NULL UNIQUE,
    rol                 VARCHAR(30) NOT NULL DEFAULT 'usuario',
    departamento        VARCHAR(100),
    telefono            VARCHAR(20),
    foto                VARCHAR(255),
    activo              TINYINT(1) NOT NULL DEFAULT 1,
    creado_en           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS core_rol (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(80) NOT NULL UNIQUE,
    descripcion TEXT,
    activo      TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS core_permiso_rol (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    rol_id      INT NOT NULL,
    modulo      VARCHAR(50) NOT NULL,
    accion      VARCHAR(20) NOT NULL,
    UNIQUE (rol_id, modulo, accion),
    CONSTRAINT fk_permiso_rol FOREIGN KEY (rol_id) REFERENCES core_rol(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS core_log_auditoria (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id      INT,
    accion          VARCHAR(20) NOT NULL,
    modelo          VARCHAR(100) NOT NULL,
    objeto_id       INT,
    descripcion     TEXT,
    ip_address      VARCHAR(45), -- Compatible con IPv6
    user_agent      TEXT,
    fecha           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_auditoria_usuario (usuario_id),
    INDEX idx_auditoria_fecha (fecha),
    INDEX idx_auditoria_modelo (modelo)
) ENGINE=InnoDB;

-- ============================================================
--  MÓDULO: RRHH
-- ============================================================

CREATE TABLE IF NOT EXISTS rrhh_departamento (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activo      TINYINT(1) NOT NULL DEFAULT 1,
    creado_en   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS rrhh_cargo (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    departamento_id INT NOT NULL,
    descripcion     TEXT,
    salario_base    DECIMAL(12,2) NOT NULL,
    activo          TINYINT(1) NOT NULL DEFAULT 1,
    creado_en       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (nombre, departamento_id),
    CONSTRAINT fk_cargo_depto FOREIGN KEY (departamento_id) REFERENCES rrhh_departamento(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS rrhh_empleado (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    cedula           VARCHAR(20) NOT NULL UNIQUE,
    nombres          VARCHAR(100) NOT NULL,
    apellidos        VARCHAR(100) NOT NULL,
    sexo             CHAR(1) NOT NULL DEFAULT 'M',
    fecha_nacimiento DATE NOT NULL,
    telefono         VARCHAR(20),
    email            VARCHAR(254),
    direccion        TEXT,
    foto             VARCHAR(255),
    cargo_id         INT NOT NULL,
    tipo_contrato    VARCHAR(20) NOT NULL DEFAULT 'indefinido',
    fecha_ingreso    DATE NOT NULL,
    fecha_egreso     DATE,
    salario          DECIMAL(12,2) NOT NULL,
    estado           VARCHAR(15) NOT NULL DEFAULT 'activo',
    usuario_id       INT UNIQUE,
    creado_por_id    INT,
    creado_en        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modificado_en    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_empleado_estado (estado),
    CONSTRAINT fk_emp_cargo FOREIGN KEY (cargo_id) REFERENCES rrhh_cargo(id)
) ENGINE=InnoDB;

-- ============================================================
--  MÓDULO: COMPRAS
-- ============================================================

CREATE TABLE IF NOT EXISTS compras_categoria_proveedor (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS compras_proveedor (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    ruc              VARCHAR(20) NOT NULL UNIQUE,
    razon_social     VARCHAR(200) NOT NULL,
    nombre_comercial VARCHAR(200),
    tipo             VARCHAR(20) NOT NULL DEFAULT 'empresa',
    categoria_id     INT,
    telefono         VARCHAR(30),
    email            VARCHAR(254),
    direccion        TEXT,
    ciudad           VARCHAR(100),
    pais             VARCHAR(100) NOT NULL DEFAULT 'Ecuador',
    dias_credito     INT NOT NULL DEFAULT 0,
    estado           VARCHAR(10) NOT NULL DEFAULT 'activo',
    creado_en        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_prov_cat FOREIGN KEY (categoria_id) REFERENCES compras_categoria_proveedor(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
--  MÓDULO: VENTAS
-- ============================================================

CREATE TABLE IF NOT EXISTS ventas_cliente (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    documento       VARCHAR(20) NOT NULL UNIQUE, -- RUC/CEDULA
    nombre          VARCHAR(200) NOT NULL,
    direccion       TEXT,
    telefono        VARCHAR(20),
    email           VARCHAR(254),
    estado          VARCHAR(10) NOT NULL DEFAULT 'activo',
    creado_en       DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ventas_producto_venta (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    nombre              VARCHAR(200) NOT NULL,
    producto_base_id    INT, -- Vínculo con Producción
    precio_unidad       DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    moneda              VARCHAR(5) DEFAULT 'USD',
    disponibilidad      TINYINT(1) NOT NULL DEFAULT 1,
    tipo_producto       VARCHAR(50), -- Limpieza Hogar, Industrial, etc.
    CONSTRAINT fk_vpt_pt FOREIGN KEY (producto_base_id) REFERENCES produccion_producto_terminado(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ventas_pedido (
    id                          INT AUTO_INCREMENT PRIMARY KEY,
    numero                      VARCHAR(20) UNIQUE,
    cliente_id                  INT NOT NULL,
    fecha_emision               DATE NOT NULL,
    dias_credito                INT NOT NULL DEFAULT 0,
    direccion_despacho          TEXT,
    iva_porcentaje              DECIMAL(5,2) NOT NULL DEFAULT 16.00,
    descuento_global_porcentaje DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    subtotal                    DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    iva_total                   DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    total                       DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    estado                      VARCHAR(15) NOT NULL DEFAULT 'borrador',
    observaciones               TEXT,
    creado_por_id               INT,
    creado_en                   DATETIME DEFAULT CURRENT_TIMESTAMP,
    modificado_en               DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (cliente_id) REFERENCES ventas_cliente(id) ON DELETE PROTECT,
    CONSTRAINT fk_pedido_creado_por FOREIGN KEY (creado_por_id) REFERENCES auth_user(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ventas_detalle_pedido (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id           INT NOT NULL,
    producto_id         INT NOT NULL,
    cantidad            DECIMAL(10,2) NOT NULL DEFAULT 1.00,
    precio_unitario     DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    subtotal_linea      DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    observaciones       TEXT,
    CONSTRAINT fk_detalle_pedido_pedido FOREIGN KEY (pedido_id) REFERENCES ventas_pedido(id) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_pedido_producto FOREIGN KEY (producto_id) REFERENCES ventas_producto_venta(id) ON DELETE PROTECT,
    UNIQUE (pedido_id, producto_id)
) ENGINE=InnoDB;

-- Tabla para trazabilidad Compras/Materia Prima
CREATE TABLE IF NOT EXISTS compras_producto_mp (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    proveedor_id        INT NOT NULL,
    materia_prima_id    INT NOT NULL,
    costo_ultimo        DECIMAL(12,4),
    referencia_interna  VARCHAR(100),
    CONSTRAINT fk_compra_mp_prov FOREIGN KEY (proveedor_id) REFERENCES compras_proveedor(id),
    CONSTRAINT fk_compra_mp_base FOREIGN KEY (materia_prima_id) REFERENCES produccion_materia_prima(id)
) ENGINE=InnoDB;

-- ============================================================
--  MÓDULO: PRODUCCIÓN
-- ============================================================

CREATE TABLE IF NOT EXISTS produccion_producto_terminado (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    codigo           VARCHAR(50) NOT NULL UNIQUE,
    nombre           VARCHAR(200) NOT NULL,
    descripcion      TEXT,
    unidad_medida    VARCHAR(20) NOT NULL DEFAULT 'unidad',
    costo_estimado   DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
    stock_actual     DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    stock_minimo     DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    activo           TINYINT(1) NOT NULL DEFAULT 1,
    creado_en        DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pt_stock (stock_actual, stock_minimo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS produccion_materia_prima (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    codigo           VARCHAR(50) NOT NULL UNIQUE,
    nombre           VARCHAR(200) NOT NULL,
    unidad_medida    VARCHAR(20) NOT NULL DEFAULT 'kg',
    costo_unitario   DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
    stock_actual     DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    stock_minimo     DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    activo           TINYINT(1) NOT NULL DEFAULT 1,
    creado_en        DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
--  VISTAS (Adaptadas a MySQL)
-- ============================================================

CREATE OR REPLACE VIEW v_empleados_activos AS
SELECT
    e.id, e.cedula,
    CONCAT(e.nombres, ' ', e.apellidos) AS nombre_completo,
    c.nombre AS cargo, d.nombre AS departamento,
    e.salario, e.estado, e.fecha_ingreso
FROM rrhh_empleado e
JOIN rrhh_cargo c ON c.id = e.cargo_id
JOIN rrhh_departamento d ON d.id = c.departamento_id
WHERE e.estado = 'activo';

CREATE OR REPLACE VIEW v_stock_bajo_mp AS
SELECT
    codigo, nombre, unidad_medida,
    stock_actual, stock_minimo,
    (stock_minimo - stock_actual) AS deficit
FROM produccion_materia_prima
WHERE activo = 1 AND stock_actual <= stock_minimo
ORDER BY deficit DESC;

-- ============================================================
--  DATOS INICIALES
-- ============================================================

INSERT IGNORE INTO rrhh_departamento (nombre, descripcion) VALUES
    ('Gerencia', 'Alta dirección'),
    ('Producción', 'Fabricación de productos'),
    ('Ventas', 'Comercialización'),
    ('Contabilidad', 'Control financiero');

INSERT IGNORE INTO compras_categoria_proveedor (nombre, descripcion) VALUES
    ('Materia Prima', 'Insumos químicos'),
    ('Empaque', 'Envases y etiquetas'),
    ('Servicios', 'Mantenimiento y logística');

SET FOREIGN_KEY_CHECKS = 1;