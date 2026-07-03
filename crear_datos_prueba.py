import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_limpieza.settings')
django.setup()

from decimal import Decimal
from django.utils import timezone
from apps.facturacion.models import Proveedor
from apps.compras.models import ProductoCompra, OrdenCompra, FacturaCompra, DetalleFacturaCompra
from apps.rrhh.models import Empleado, Nomina, NominaDetalle
from django.contrib.auth import get_user_model

User = get_user_model()

def generar_datos():
    print("Iniciando generación de datos de prueba...")

    # 1. Crear un usuario de prueba (si no existe)
    user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
    if created:
        user.set_password('admin123')
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print("Usuario 'admin' creado con contraseña 'admin123'.")

    # 2. Datos de Compra (Proveedor, Producto, Orden y Factura)
    proveedor, _ = Proveedor.objects.get_or_create(
        rif='J-12345678-9',
        defaults={'razon_social': 'Insumos Limpieza CA', 'direccion': 'Caracas', 'telefono': '0212-5555555'}
    )
    
    producto_compra, _ = ProductoCompra.objects.get_or_create(
        codigo='MAT-001',
        defaults={'nombre': 'Cloro Líquido (Tambor)', 'precio_referencia': Decimal('50.00')}
    )
    
    orden_compra, _ = OrdenCompra.objects.get_or_create(
        numero='OC-0001',
        defaults={'proveedor': proveedor, 'total': Decimal('58.00'), 'estado': 'aprobada'}
    )

    factura_compra, _ = FacturaCompra.objects.get_or_create(
        numero_factura='FAC-1001',
        proveedor=proveedor,
        defaults={
            'orden_compra': orden_compra,
            'numero_control': '00-001234',
            'fecha_emision': timezone.now().date(),
            'base_imponible': Decimal('50.00'),
            'monto_iva_general': Decimal('8.00'),
            'total': Decimal('58.00'),
            'registrada_por': user
        }
    )

    DetalleFacturaCompra.objects.get_or_create(
        factura=factura_compra,
        descripcion='Cloro Líquido (Tambor)',
        defaults={
            'cantidad': Decimal('1.00'),
            'precio_unitario': Decimal('50.00'),
            'tipo_impuesto': 'general',
            'subtotal': Decimal('58.00')
        }
    )
    print("Datos de compras fiscales (Proveedores, Facturas) generados.")

    # 3. Datos de Nómina (Empleado y Cálculo)
    empleado, _ = Empleado.objects.get_or_create(
        cedula='V-12345678',
        defaults={
            'nombres': 'Juan',
            'apellidos': 'Perez',
            'salario_base': Decimal('3000.00'), # Salario mensual
            'fecha_ingreso': timezone.now().date().replace(year=2023, month=1, day=1),
            'cargo': 'Operario'
        }
    )

    nomina, _ = Nomina.objects.get_or_create(
        fecha_inicio=timezone.now().date().replace(day=1),
        fecha_fin=timezone.now().date().replace(day=15),
        defaults={
            'descripcion': 'Nómina 1era Quincena',
            'estado': 'borrador'
        }
    )

    detalle_nomina, _ = NominaDetalle.objects.get_or_create(
        nomina=nomina,
        empleado=empleado,
        defaults={
            'salario_devengado': Decimal('1500.00'), # Quincenal
            'dias_trabajados': 15
        }
    )
    # Ejecutamos el cálculo de ley (IVSS, FAOV, INCES, Paro Forzoso)
    detalle_nomina.calcular_ley()
    print("Datos de nómina (Empleado, Recibo Quincenal con deducciones de ley) generados.")

    print("Generación de datos finalizada con éxito. Puede revisar la interfaz administrativa.")

if __name__ == '__main__':
    generar_datos()
