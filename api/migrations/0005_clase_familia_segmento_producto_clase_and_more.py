# Generated by Django 5.1 on 2024-12-17 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_usuario_contrasena'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clase',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Codigo', models.IntegerField(blank=True, db_column='Codigo', null=True)),
                ('Descripcion', models.CharField(blank=True, db_column='Descripcion', max_length=100, null=True)),
                ('Segmento', models.IntegerField(blank=True, db_column='Segmento', null=True)),
            ],
            options={
                'db_table': 'Clase',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Familia',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Codigo', models.IntegerField(blank=True, db_column='Codigo', null=True)),
                ('Descripcion', models.CharField(blank=True, db_column='Descripcion', max_length=100, null=True)),
            ],
            options={
                'db_table': 'Familia',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Segmento',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Codigo', models.IntegerField(blank=True, db_column='Codigo', null=True)),
                ('Descripcion', models.CharField(blank=True, db_column='Descripcion', max_length=100, null=True)),
                ('Familia', models.IntegerField(blank=True, db_column='Familia', null=True)),
            ],
            options={
                'db_table': 'Segmento',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='producto',
            name='Clase',
            field=models.IntegerField(blank=True, db_column='Clase', null=True),
        ),
        migrations.AddField(
            model_name='producto',
            name='Codigo_repr',
            field=models.CharField(blank=True, db_column='Codigo_repr', max_length=100, null=True),
        ),
    ]
