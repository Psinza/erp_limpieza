#!/usr/bin/env bash
# ============================================================
#  ERP FÁBRICA DE PRODUCTOS DE LIMPIEZA
#  Script de instalación y configuración inicial
#  Uso: bash setup_erp.sh
# ============================================================

set -e   # Detener si hay error

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║     ERP Fábrica de Productos de Limpieza — Setup    ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── 1. Verificar Python ──────────────────────────────────────
echo "▶ Verificando requisitos..."
python3 --version || { echo "❌ ERROR: Python 3 no encontrado."; exit 1; }
command -v psql >/dev/null 2>&1 || { echo "❌ ERROR: PostgreSQL (psql) no está instalado."; exit 1; }

# ── 2. Crear entorno virtual ─────────────────────────────────
echo "▶ Preparando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# ── 3. Instalar dependencias ─────────────────────────────────
echo "▶ Instalando dependencias Python..."
pip install --upgrade pip
pip install \
    django==4.2.* \
    psycopg2-binary==2.9.* \
    djangorestframework==3.14.* \
    djangorestframework-simplejwt==5.3.* \
    django-cors-headers==4.3.* \
    whitenoise==6.6.* \
    Pillow==10.* \
    python-decouple==3.8 \
    dj-database-url==2.1.*

echo "▶ Dependencias instaladas correctamente."

# ── 4. Configurar variables de entorno ───────────────────────
echo "▶ Configurando .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    # Generar SECRET_KEY automáticamente
    SECRET=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    sed -i "s|django-insecure-erp-limpieza-cambiar-en-produccion.*|${SECRET}|g" .env
    echo "  ✔ Archivo .env creado. Edítalo con tus credenciales de BD."
else
    echo "  ✔ .env ya existe, se mantiene."
fi

# ── 5. Crear base de datos PostgreSQL ────────────────────────
echo ""
echo "▶ Configurando PostgreSQL..."
echo "  Ingresa las credenciales del superusuario de PostgreSQL:"
read -p "  Usuario PostgreSQL (ej: postgres): " PG_USER
read -s -p "  Contraseña PostgreSQL: " PG_PASS
echo ""

# Crear BD y usuario
PGPASSWORD="$PG_PASS" psql -U "$PG_USER" -c "
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'erp_user') THEN
        CREATE USER erp_user WITH PASSWORD 'Erp\$2025#Limpieza' CREATEDB NOSUPERUSER;
    END IF;
END
\$\$;
" 2>/dev/null || true

PGPASSWORD="$PG_PASS" psql -U "$PG_USER" -c "
SELECT 'CREATE DATABASE erp_limpieza OWNER erp_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'erp_limpieza')
\gexec
" 2>/dev/null || true

PGPASSWORD="$PG_PASS" psql -U "$PG_USER" -c "
GRANT ALL PRIVILEGES ON DATABASE erp_limpieza TO erp_user;
" 2>/dev/null || true

echo "  ✔ Base de datos 'erp_limpieza' y usuario 'erp_user' configurados."

# ── 6. Migraciones Django ─────────────────────────────────────
echo ""
echo "▶ Ejecutando migraciones..."
python manage.py makemigrations --no-input
python manage.py migrate --no-input
echo "  ✔ Migraciones completadas."

# ── 7. Cargar datos iniciales ─────────────────────────────────
echo "▶ Ejecutando script SQL de datos iniciales..."
PGPASSWORD="Erp\$2025#Limpieza" psql -U erp_user -d erp_limpieza \
    -f database/erp_limpieza_schema.sql \
    --set ON_ERROR_STOP=off \
    -q 2>/dev/null || true
echo "  ✔ Datos iniciales cargados."

# ── 8. Colectar estáticos ─────────────────────────────────────
echo "▶ Colectando archivos estáticos..."
python manage.py collectstatic --no-input --clear 2>/dev/null || true

# ── 9. Crear superusuario ─────────────────────────────────────
echo ""
echo "▶ Crear superusuario del ERP:"
python manage.py createsuperuser

# ── 10. Crear directorio de logs ─────────────────────────────
mkdir -p logs
echo "  ✔ Directorio 'logs/' creado."

# ── Resumen ───────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║             ✅  INSTALACIÓN COMPLETADA               ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Iniciar servidor:  python manage.py runserver       ║"
echo "║  URL del ERP:       http://localhost:8000            ║"
echo "║  Panel Admin:       http://localhost:8000/admin      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
