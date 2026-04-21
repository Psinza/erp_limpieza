from django.db import models

class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Cargo(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='cargos')
    salario_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def __str__(self): return self.nombre

class Empleado(models.Model):
    cedula = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, null=True)
    sueldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fecha_ingreso = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class Nomina(models.Model):
    MESES = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre'),
    ]
    mes = models.IntegerField(choices=MESES)
    anio = models.IntegerField(default=2024)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    total_nomina = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=[('borrador', 'Borrador'), ('pagada', 'Pagada')], default='borrador')

    def __str__(self):
        return f"Nómina {self.get_mes_display()} {self.anio}"

class NominaDetalle(models.Model):
    nomina = models.ForeignKey(Nomina, related_name='detalles', on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    sueldo_base = models.DecimalField(max_digits=10, decimal_places=2)
    ingresos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    egresos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    neto_recibir = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle {self.empleado} - {self.nomina}"

class Vacacion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_solicitados = models.IntegerField()
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada')], default='pendiente')
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Vacaciones {self.empleado} ({self.fecha_inicio})"