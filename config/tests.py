from django.test import TestCase
from apps.activos_fijos.models import ActivoFijo
from datetime import date

class ActivoFijoTest(TestCase):
    def setUp(self):
        self.activo = ActivoFijo.objects.create(
            codigo="MAQ-001",
            nombre="Mezcladora Industrial 500L",
            fecha_adquisicion=date.today(),
            valor_compra=5000.00,
            vida_util_meses=60
        )

    def test_creacion_activo(self):
        """Verifica que el activo se guarde correctamente"""
        self.assertEqual(self.activo.codigo, "MAQ-001")
        self.assertEqual(self.activo.estado, "operativo")