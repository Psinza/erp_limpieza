from django.core.management.base import BaseCommand
from django.db import transaction
from apps.rrhh.models import Departamento, Cargo, Empleado
from apps.contabilidad.models import EjercicioContable, CuentaContable
from apps.activos_fijos.models import ActivoFijo
from datetime import date

class Command(BaseCommand):
    help = 'Carga datos de prueba iniciales para los módulos de RRHH y Contabilidad'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando la carga de datos de prueba...'))

        try:
            with transaction.atomic():
                # --- RRHH ---
                # 1. Departamentos (Complementando los existentes en el SQL inicial)
                admin_depto, _ = Departamento.objects.get_or_create(
                    nombre='Administración',
                    defaults={'descripcion': 'Gestión administrativa y servicios generales'}
                )
                
                # 2. Cargos
                # Asumimos que 'Gerencia' ya existe por el script SQL inicial
                gerencia = Departamento.objects.get(nombre='Gerencia')
                gerente_finanzas, _ = Cargo.objects.get_or_create(
                    nombre='Gerente de Finanzas',
                    departamento=gerencia,
                    defaults={'salario_base': 4500.00}
                )
                analista_rrhh, _ = Cargo.objects.get_or_create(
                    nombre='Analista de RRHH',
                    departamento=admin_depto,
                    defaults={'salario_base': 1800.00}
                )

                # 3. Empleados de prueba
                Empleado.objects.get_or_create(
                    cedula='V-10200300',
                    defaults={
                        'nombres': 'Ana',
                        'apellidos': 'Martínez',
                        'sexo': 'F',
                        'fecha_nacimiento': date(1988, 3, 10),
                        'cargo': gerente_finanzas,
                        'fecha_ingreso': date(2023, 1, 15),
                        'salario': 4500.00,
                        'estado': 'activo'
                    }
                )

                # --- CONTABILIDAD ---
                # 4. Ejercicio Contable
                ejercicio, _ = EjercicioContable.objects.get_or_create(
                    nombre='Ejercicio Fiscal 2025',
                    defaults={
                        'fecha_inicio': date(2025, 1, 1),
                        'fecha_fin': date(2025, 12, 31),
                        'abierto': True
                    }
                )

                # 5. Plan de Cuentas Básico
                cuentas = [
                    ('1', 'ACTIVOS', 'activo', 'deudora', None),
                    ('1.1', 'Activo Corriente', 'activo', 'deudora', '1'),
                    ('1.1.01', 'Caja Principal', 'activo', 'deudora', '1.1'),
                    ('1.1.02', 'Bancos Locales', 'activo', 'deudora', '1.1'),
                    ('2', 'PASIVOS', 'pasivo', 'acreedora', None),
                    ('3', 'PATRIMONIO', 'patrimonio', 'acreedora', None),
                    ('4', 'INGRESOS', 'ingreso', 'acreedora', None),
                    ('5', 'COSTOS', 'costo', 'deudora', None),
                    ('6', 'GASTOS', 'egreso', 'deudora', None),
                ]

                for cod, nom, tipo, nat, padre_cod in cuentas:
                    padre = CuentaContable.objects.filter(codigo=padre_cod).first() if padre_cod else None
                    CuentaContable.objects.get_or_create(
                        codigo=cod,
                        defaults={'nombre': nom, 'tipo': tipo, 'naturaleza': nat, 'padre': padre}
                    )

                # --- ACTIVOS FIJOS ---
                ActivoFijo.objects.get_or_create(
                    codigo="MAQ-001",
                    defaults={
                        'nombre': 'Mezcladora Industrial 500L',
                        'fecha_adquisicion': date(2024, 1, 10),
                        'valor_compra': 5000.00,
                        'vida_util_meses': 60
                    }
                )

            self.stdout.write(self.style.SUCCESS('¡Datos de prueba cargados exitosamente!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la carga: {str(e)}'))