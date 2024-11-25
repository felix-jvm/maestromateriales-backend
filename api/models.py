from django.db import models

class Usuario(models.Model):
    ID = models.AutoField(primary_key=True)
    Nombre = models.CharField(db_column='Nombre', max_length=50, blank=False, null=False) 
    Contrasena = models.BinaryField(db_column='Contrasena', blank=False, null=False)
    Activo = models.BooleanField(db_column='Activo', default=True, blank=False, null=False)    
    PermisoNivel = models.IntegerField(db_column='PermisoNivel', blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'Usuario'    

class PermisoNivel(models.Model):
    ID = models.AutoField(primary_key=True)
    Nivel = models.IntegerField(db_column='Nivel', blank=False, null=False)
    Descripcion = models.CharField(db_column='Descripcion', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'PermisoNivel'

class UsuarioCodigo(models.Model):
    ID = models.AutoField(primary_key=True)
    Codigo = models.CharField(db_column='Codigo', max_length=100, blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'UsuarioCodigo'

class Producto(models.Model):
    ID = models.AutoField(primary_key=True)
    Codigo = models.CharField(db_column='Codigo', max_length=100, blank=False, null=False)
    Descripcion = models.CharField(db_column='Descripcion', max_length=500, blank=True, null=True)
    UnidadMedida = models.IntegerField(db_column='UnidadMedida', blank=True, null=True)
    Categoria = models.IntegerField(db_column='Categoria', blank=True, null=True)
    EstadoMaterial = models.IntegerField(db_column='EstadoMaterial', blank=True, null=True)
    Minimo = models.IntegerField(db_column='Minimo', blank=True, null=True)
    Maximo = models.IntegerField(db_column='Maximo', blank=True, null=True)
    PuntoReorden = models.IntegerField(db_column='PuntoReorden', blank=True, null=True)
    Proveedor = models.IntegerField(db_column='Proveedor', blank=True, null=True)
    TiempoEntrega = models.IntegerField(db_column='TiempoEntrega', blank=True, null=True)
    PedidoEstandar = models.IntegerField(db_column='PedidoEstandar', blank=True, null=True)
    LoteMinimo = models.IntegerField(db_column='LoteMinimo', blank=True, null=True)
    LoteMaximo = models.IntegerField(db_column='LoteMaximo', blank=True, null=True)
    TiempoProcesoInterno = models.IntegerField(db_column='TiempoProcesoInterno', blank=True, null=True)
    TiempoVidaUtil = models.IntegerField(db_column='TiempoVidaUtil', blank=True, null=True)
    FichaTecnica = models.BinaryField(db_column='FichaTecnica', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Producto'    

class Categoria(models.Model):
    ID = models.AutoField(primary_key=True)
    Descripcion = models.CharField(db_column='Descripcion', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Categoria'    

class UnidadMedida(models.Model):
    ID = models.AutoField(primary_key=True)
    Descripcion = models.CharField(db_column='Descripcion', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'UnidadMedida'    

class EstadoMaterial(models.Model):
    ID = models.AutoField(primary_key=True)
    Descripcion = models.CharField(db_column='Descripcion', max_length=100, blank=True, null=True)    

    class Meta:
        managed = True
        db_table = 'EstadoMaterial'    

class Proveedor(models.Model):
    ID = models.AutoField(primary_key=True)
    Descripcion = models.CharField(db_column='Descripcion', max_length=100, blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'Proveedor'    

