"""
Comando: python manage.py init_erp

Crea las áreas, roles predeterminados y el superusuario administrador.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.core.models import Area, Rol, Permiso, Usuario


AREAS_INICIALES = [
    ('RRHH',       'Recursos Humanos'),
    ('ADMIN',      'Administración'),
    ('COMPRAS',    'Compras'),
    ('VENTAS',     'Ventas'),
    ('TESORERIA',  'Tesorería'),
    ('ORD_PAGOS',  'Ordenación de Pagos'),
    ('CONTAB',     'Contabilidad'),
    ('PRODUCCION', 'Producción'),
    ('COMERCIAL',  'Comercialización'),
    ('LOGISTICA',  'Logística'),
    ('ALMACEN_MP', 'Almacén Materias Primas'),
    ('ALMACEN_PT', 'Almacén Productos Terminados'),
    ('TRANSPORTE', 'Transportes'),
    ('VENDEDORES', 'Vendedores'),
]

ROLES_INICIALES = [
    {
        'nombre': 'Administrador',
        'nivel': 'SUPERUSUARIO',
        'descripcion': 'Acceso total al sistema',
        'areas': [c for c, _ in AREAS_INICIALES],
        'permisos': ['ver', 'crear', 'editar', 'eliminar', 'aprobar', 'exportar', 'reportar'],
    },
    {
        'nombre': 'RRHH',
        'nivel': 'LECTURA_ESCRITURA',
        'descripcion': 'Gestión de personal y nómina',
        'areas': ['RRHH'],
        'permisos': ['ver', 'crear', 'editar', 'exportar', 'reportar'],
    },
    {
        'nombre': 'Jefe de Compras',
        'nivel': 'APROBADOR',
        'descripcion': 'Gestión y aprobación de compras',
        'areas': ['COMPRAS', 'ALMACEN_MP'],
        'permisos': ['ver', 'crear', 'editar', 'aprobar', 'exportar', 'reportar'],
    },
    {
        'nombre': 'Jefe de Ventas',
        'nivel': 'APROBADOR',
        'descripcion': 'Gestión de ventas y comercialización',
        'areas': ['VENTAS', 'COMERCIAL', 'VENDEDORES'],
        'permisos': ['ver', 'crear', 'editar', 'aprobar', 'exportar', 'reportar'],
    },
    {
        'nombre': 'Tesorero',
        'nivel': 'APROBADOR',
        'descripcion': 'Control de caja y pagos',
        'areas': ['TESORERIA', 'ORD_PAGOS'],
        'permisos': ['ver', 'crear', 'editar', 'aprobar', 'reportar'],
    },
    {
        'nombre': 'Contador',
        'nivel': 'LECTURA_ESCRITURA',
        'descripcion': 'Registro contable y reportes',
        'areas': ['CONTAB'],
        'permisos': ['ver', 'crear', 'editar', 'exportar', 'reportar'],
    },
    {
        'nombre': 'Jefe de Producción',
        'nivel': 'SUPERVISOR',
        'descripcion': 'Control de producción y calidad',
        'areas': ['PRODUCCION', 'ALMACEN_MP', 'ALMACEN_PT'],
        'permisos': ['ver', 'crear', 'editar', 'reportar'],
    },
    {
        'nombre': 'Jefe de Logística',
        'nivel': 'SUPERVISOR',
        'descripcion': 'Control de almacenes y despacho',
        'areas': ['LOGISTICA', 'ALMACEN_MP', 'ALMACEN_PT', 'TRANSPORTE'],
        'permisos': ['ver', 'crear', 'editar', 'exportar', 'reportar'],
    },
    {
        'nombre': 'Vendedor',
        'nivel': 'LECTURA_ESCRITURA',
        'descripcion': 'Registro de pedidos y seguimiento',
        'areas': ['VENTAS', 'VENDEDORES', 'COMERCIAL'],
        'permisos': ['ver', 'crear', 'editar'],
    },
    {
        'nombre': 'Transportista',
        'nivel': 'SOLO_LECTURA',
        'descripcion': 'Consulta de rutas y despachos',
        'areas': ['TRANSPORTE', 'ALMACEN_PT'],
        'permisos': ['ver'],
    },
]


class Command(BaseCommand):
    help = 'Inicializa el ERP: crea áreas, roles y superusuario admin'

    def add_arguments(self, parser):
        parser.add_argument('--admin-password', default='Admin1234!',
                            help='Contraseña del superusuario (default: Admin1234!)')

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Iniciando ERP Limpieza Industrial ===\n'))

        # 1. Áreas
        self.stdout.write('  Creando áreas...')
        area_map = {}
        for codigo, nombre in AREAS_INICIALES:
            area, created = Area.objects.get_or_create(
                codigo=codigo, defaults={'nombre': nombre}
            )
            area_map[codigo] = area
            self.stdout.write(f'    {"[OK]" if created else "[ya existía]"} {nombre}')

        # 2. Roles y permisos
        self.stdout.write('\n  Creando roles y permisos...')
        for r_data in ROLES_INICIALES:
            rol, created = Rol.objects.get_or_create(
                nombre=r_data['nombre'],
                defaults={
                    'nivel': r_data['nivel'],
                    'descripcion': r_data['descripcion'],
                }
            )
            rol.areas.set([area_map[c] for c in r_data['areas'] if c in area_map])

            for area_codigo in r_data['areas']:
                if area_codigo not in area_map:
                    continue
                for accion in r_data['permisos']:
                    Permiso.objects.get_or_create(
                        rol=rol, area=area_map[area_codigo], accion=accion
                    )
            self.stdout.write(f'    {"[OK]" if created else "[ya existía]"} {rol.nombre}')

        # 3. Superusuario
        self.stdout.write('\n  Creando superusuario...')
        admin_password = options['admin_password']
        admin_area = area_map.get('ADMIN')
        admin_rol = Rol.objects.filter(nombre='Administrador').first()

        if not Usuario.objects.filter(username='admin').exists():
            Usuario.objects.create_superuser(
                username='admin',
                email='admin@erplimp.com',
                password=admin_password,
                nombres='Administrador',
                apellidos='Sistema',
                area=admin_area,
                rol=admin_rol,
                cargo='Administrador del Sistema',
            )
            self.stdout.write(f'    [OK] usuario: admin / contraseña: {admin_password}')
        else:
            self.stdout.write('    [ya existía] usuario admin')

        self.stdout.write(self.style.SUCCESS('\n=== ERP inicializado correctamente ===\n'))
        self.stdout.write('  Ejecute: python manage.py runserver')
        self.stdout.write('  Acceda a: http://localhost:8000/core/login/\n')
