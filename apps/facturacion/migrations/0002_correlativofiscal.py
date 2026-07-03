from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CorrelativoFiscal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('factura', 'Factura'), ('control', 'Número de Control'), ('nota_entrega', 'Nota de Entrega'), ('presupuesto', 'Presupuesto/Pedido')], max_length=20, unique=True)),
                ('prefijo', models.CharField(blank=True, max_length=10)),
                ('proximo_numero', models.PositiveIntegerField(default=1)),
                ('longitud_ceros', models.PositiveIntegerField(default=6, help_text='Cantidad de ceros a la izquierda')),
            ],
            options={
                'verbose_name': 'Correlativo Fiscal',
                'verbose_name_plural': 'Correlativos Fiscales',
            },
        ),
    ]
