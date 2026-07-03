from django.db import models
from django.utils import timezone
from decimal import Decimal
from dateutil.relativedelta import relativedelta

class Departamento(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Departamento")
    activo = models.BooleanField(default=True)

    @property
    def num_cargos(self):
        return self.cargos.count()

    def __str__(self):
        return self.nombre

class Cargo(models.Model):
    NIVELES_CARGO = [
        ('profesional', 'Nivel Profesional y Técnico'),
        ('supervision', 'Nivel de Supervisión y Dirección'),
        ('estrategico', 'Niveles Estratégicos y Gerenciales'),
        ('operativo', 'Niveles Operativos y Especialistas'),
    ]
    SECTOR_CHOICES = [
        ('publico', 'Sector Público (A.P.N)'),
        ('privado', 'Sector Privado'),
        ('mixto', 'Mixto / General'),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Nombre del Cargo")
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='cargos')
    nivel = models.CharField(max_length=20, choices=NIVELES_CARGO, default='operativo', verbose_name="Nivel Jerárquico")
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES, default='privado', verbose_name="Sector de Referencia")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción de Funciones")
    salario_base_referencial = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Salario Base Ref.")
    
    def __str__(self): 
        return f"{self.nombre} - {self.departamento.nombre}"

class Empleado(models.Model):
    NACIONALIDAD_CHOICES = [('V', 'Venezolano'), ('E', 'Extranjero')]
    CONTRATO_CHOICES = [
        ('IND', 'Tiempo Indeterminado'),
        ('DET', 'Tiempo Determinado'),
        ('OBR', 'Por Obra Determinada')
    ]

    nacionalidad = models.CharField(max_length=1, choices=NACIONALIDAD_CHOICES, default='V', verbose_name="Nacionalidad")
    cedula = models.CharField(max_length=15, unique=True, verbose_name="Cédula de Identidad")
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    
    # Nuevos campos personales y de contacto
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección de Habitación")
    telefono = models.CharField(max_length=100, blank=True, null=True, verbose_name="Números de Contacto")
    grado_instruccion = models.CharField(max_length=100, blank=True, null=True, verbose_name="Grado de Instrucción")
    
    # Salud y Biometría
    tipo_sangre = models.CharField(max_length=10, blank=True, null=True, verbose_name="Tipo de Sangre")
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    estatura = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Estatura (m)")
    enfermedades = models.TextField(blank=True, null=True, verbose_name="Enfermedades Preexistentes")
    discapacidad = models.TextField(blank=True, null=True, verbose_name="Discapacidades (Si aplica)")
    
    # Tallas para Uniformes (Dotación)
    talla_camisa = models.CharField(max_length=10, blank=True, null=True, verbose_name="Talla de Camisa")
    talla_pantalon = models.CharField(max_length=10, blank=True, null=True, verbose_name="Talla de Pantalón")
    talla_calzado = models.CharField(max_length=10, blank=True, null=True, verbose_name="Talla de Calzado")

    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, verbose_name="Departamento")
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, null=True, verbose_name="Cargo")
    tipo_contrato = models.CharField(max_length=3, choices=CONTRATO_CHOICES, default='IND', verbose_name="Tipo de Contrato")
    
    salario_base = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Salario Base (VES)")
    bono_alimentacion = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Cesta Ticket / Bono Alimentación (VES)")
    bono_divisas = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Bono Complementario (USD)")
    
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso")
    fecha_egreso = models.DateField(blank=True, null=True, verbose_name="Fecha de Egreso")
    cargas_familiares = models.IntegerField(default=0, verbose_name="Cargas Familiares")
    cuenta_bancaria = models.CharField(max_length=20, blank=True, null=True, verbose_name="Cuenta Bancaria (20 dígitos)")
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('vacaciones', 'Vacaciones'),
        ('baja', 'Baja/Egreso'),
    ]
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='activo', verbose_name="Estado del Empleado")
    activo = models.BooleanField(default=True, verbose_name="Habilitado para Sistema")

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    def antiguedad_anios(self):
        hoy = timezone.now().date()
        return relativedelta(hoy, self.fecha_ingreso).years

    def __str__(self):
        return f"{self.nacionalidad}-{self.cedula} {self.nombres} {self.apellidos}"

class Nomina(models.Model):
    TIPO_NOMINA_CHOICES = [
        ('Q1', 'Primera Quincena'),
        ('Q2', 'Segunda Quincena'),
        ('MEN', 'Mensual'),
        ('VAC', 'Vacaciones'),
        ('UTI', 'Utilidades (Aguinaldos)'),
        ('LIQ', 'Liquidación')
    ]
    MESES = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre'),
    ]
    
    tipo = models.CharField(max_length=3, choices=TIPO_NOMINA_CHOICES, default='Q1', verbose_name="Tipo de Nómina")
    mes = models.IntegerField(choices=MESES, verbose_name="Mes correspondiente")
    anio = models.IntegerField(default=timezone.now().year, verbose_name="Año")
    tasa_bcv = models.DecimalField(max_digits=14, decimal_places=4, default=1.0000, verbose_name="Tasa BCV aplicable")
    
    fecha_generacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Generación")
    total_asignaciones = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Total Asignaciones")
    total_deducciones = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Total Deducciones")
    total_nomina = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Total Neto a Pagar")
    estado = models.CharField(max_length=20, choices=[('BORRADOR', 'Borrador'), ('PROCESADA', 'Procesada'), ('PAGADA', 'Pagada')], default='BORRADOR')

    class Meta:
        ordering = ['-anio', '-mes']
        verbose_name = "Nómina"
        verbose_name_plural = "Nóminas"

    def __str__(self):
        return f"Nómina {self.get_tipo_display()} - {self.get_mes_display()} {self.anio}"

class NominaDetalle(models.Model):
    nomina = models.ForeignKey(Nomina, related_name='detalles', on_delete=models.CASCADE, verbose_name="Nómina")
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, verbose_name="Empleado")
    
    # Asignaciones
    sueldo_base = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Sueldo Base")
    bono_alimentacion = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Cesta Ticket")
    horas_extras = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Horas Extras")
    bono_produccion = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Bonos / Otros Ingresos")
    
    # Deducciones de Ley (LOTTT/Seguridad Social)
    ivss = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Retención IVSS (4%)")
    faov = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Retención FAOV (1%)")
    paro_forzoso = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Retención SPF (0.5%)")
    inces = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Retención INCES (0.5%)")
    otras_deducciones = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Otras Deducciones")
    
    total_asignaciones = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Total Asignaciones")
    total_deducciones = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Total Deducciones")
    neto_recibir = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Neto a Recibir")

    class Meta:
        verbose_name = "Recibo de Pago"
        verbose_name_plural = "Recibos de Pago"

    def calcular_ley(self):
        # Cálculos estándar según leyes venezolanas sobre el sueldo base
        self.ivss = self.sueldo_base * Decimal('0.04')
        self.faov = self.sueldo_base * Decimal('0.01')
        self.paro_forzoso = self.sueldo_base * Decimal('0.005')
        self.inces = self.sueldo_base * Decimal('0.005')
        
        self.total_asignaciones = self.sueldo_base + self.bono_alimentacion + self.horas_extras + self.bono_produccion
        self.total_deducciones = self.ivss + self.faov + self.paro_forzoso + self.inces + self.otras_deducciones
        self.neto_recibir = self.total_asignaciones - self.total_deducciones
        self.save()

    def __str__(self):
        return f"Recibo {self.empleado.nombres} - {self.nomina}"

class Vacacion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, verbose_name="Empleado")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    dias_disfrute = models.IntegerField(default=15, verbose_name="Días Hábiles de Disfrute")
    bono_vacacional_dias = models.IntegerField(default=15, verbose_name="Días de Bono Vacacional (Art. 192)")
    estado = models.CharField(max_length=20, choices=[('PENDIENTE', 'Pendiente'), ('APROBADA', 'Aprobada'), ('DISFRUTADA', 'Disfrutada')], default='PENDIENTE')
    observaciones = models.TextField(blank=True, null=True)

    @property
    def dias_solicitados(self):
        if self.fecha_inicio and self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).days + 1
        return 0

    class Meta:
        verbose_name = "Vacación"
        verbose_name_plural = "Vacaciones"

    def __str__(self):
        return f"Vacaciones {self.empleado} ({self.fecha_inicio})"

class PrestacionSocial(models.Model):
    """
    Control de Prestaciones Sociales / Fideicomiso (Art. 142 LOTTT).
    """
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, verbose_name="Empleado")
    trimestre = models.CharField(max_length=10, help_text="Ej: 2024-Q1", verbose_name="Trimestre")
    salario_integral_diario = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Salario Integral Diario")
    dias_abonados = models.IntegerField(default=15, verbose_name="Días Abonados (Art. 142)")
    monto_abonado = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Monto Abonado")
    anticipos = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Anticipos")

    class Meta:
        verbose_name = "Prestación Social"
        verbose_name_plural = "Prestaciones Sociales"

    def __str__(self):
        return f"Fideicomiso {self.empleado.cedula} - {self.trimestre}"

class CestaTicketRecibo(models.Model):
    """
    Recibo de Cestaticket Socialista, separado de la nómina regular.
    """
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, verbose_name="Empleado")
    mes = models.IntegerField(choices=Nomina.MESES, verbose_name="Mes")
    anio = models.IntegerField(default=timezone.now().year, verbose_name="Año")
    dias_trabajados = models.IntegerField(default=30, verbose_name="Días Laborados")
    monto_mensual_ley = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Monto Cestaticket")
    monto_pagado = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Monto a Pagar")
    fecha_emision = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[('GENERADO', 'Generado'), ('PAGADO', 'Pagado')], default='GENERADO')

    class Meta:
        verbose_name = "Recibo de Cestaticket"
        verbose_name_plural = "Recibos de Cestaticket"

    def __str__(self):
        return f"Cestaticket {self.empleado.nombres} - {self.mes}/{self.anio}"

class Utilidad(models.Model):
    """
    Cálculo de Utilidades (Aguinaldos) de fin de año.
    """
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, verbose_name="Empleado")
    anio = models.IntegerField(default=timezone.now().year, verbose_name="Año Fiscal")
    dias_utilidad = models.IntegerField(default=30, verbose_name="Días de Utilidades (Min 30)")
    salario_promedio = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Salario Promedio")
    monto_pagar = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Monto Utilidades")
    fecha_pago = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Utilidad (Aguinaldo)"
        verbose_name_plural = "Utilidades"

    def __str__(self):
        return f"Utilidades {self.anio} - {self.empleado.nombres}"

class Liquidacion(models.Model):
    """
    Cálculo de liquidación de prestaciones sociales por término de relación laboral.
    """
    empleado = models.OneToOneField(Empleado, on_delete=models.CASCADE, verbose_name="Empleado")
    fecha_egreso = models.DateField(verbose_name="Fecha de Egreso")
    motivo_egreso = models.CharField(max_length=50, choices=[('RENUNCIA', 'Renuncia Voluntaria'), ('DESPIDO_J', 'Despido Justificado'), ('DESPIDO_I', 'Despido Injustificado')], default='RENUNCIA')
    
    salario_integral_diario = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Salario Integral Diario")
    
    # Conceptos
    prestaciones_acumuladas = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Fideicomiso Acumulado")
    vacaciones_fraccionadas = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Vacaciones Fraccionadas")
    bono_vacacional_fraccionado = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Bono Vacacional Fraccionado")
    utilidades_fraccionadas = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Utilidades Fraccionadas")
    indemnizacion = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Indemnización (Art. 92)")
    
    total_liquidacion = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Total Liquidación")
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Liquidación"
        verbose_name_plural = "Liquidaciones"

    def __str__(self):
        return f"Liquidación {self.empleado.nombres} - {self.fecha_egreso}"