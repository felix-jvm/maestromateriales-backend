from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from django.conf.urls.static import static
from django.http import HttpResponse
from django.http import FileResponse
from rest_framework import viewsets
from django.conf import settings
from django.contrib import admin
from django.urls import path
import api.models as M
import pandas as pd
import psycopg2
import bcrypt
import magic
import json
import os

class ProductoView(viewsets.ViewSet):
 
 def create(self,req):
  if req.data['mode'] == 'fillForm':
   selectRecords = {'UnidadMedida':[],'Categoria':[],'EstadoMaterial':[],'Proveedor':[]}
   for model in selectRecords.keys():
    modelRecords = eval('M.%s'%(model)).objects.all().values('ID','Descripcion')
    if modelRecords:selectRecords[model] = modelRecords
   if type(req.data['productCode']) == str and 'updt' in req.data['productCode']:
    productCodigo = req.data['productCode'].split('_')[1].replace(' ','').strip()
    selectRecords['specificRecord'] = list(M.Producto.objects.filter(Codigo=productCodigo).values('Codigo','Descripcion','UnidadMedida','Categoria','EstadoMaterial','Minimo','Maximo','PuntoReorden','Proveedor','TiempoEntrega','PedidoEstandar','LoteMinimo','LoteMaximo','TiempoProcesoInterno','TiempoVidaUtil','FichaTecnica'))
    selectRecords['specificRecord'][0]['FichaTecnica'] = 'True' if selectRecords['specificRecord'][0]['FichaTecnica'] else 'False'
   return Response(selectRecords)
  if req.data['mode'] == 'create':
   if 'updt_producto_codigo' in req.data['payload']:
    # if 'codeChanged' in req.data['payload'].keys() and req.data['payload']['codeChanged']:
    #  codeToLook = req.data['payload']['Codigo']
    #  foundRecord = list(M.Producto.objects.filter(Codigo=codeToLook))
    #  if foundRecord:return Response({'msg':'El código %s esta siendo usado por el producto: %s'%(codeToLook,foundRecord[0].Descripcion)})
    recordToUpdt = M.Producto.objects.filter(Codigo=req.data['payload']['updt_producto_codigo'])
    dictRepr = {}
    for propToUpdt in req.data['payload'].keys():
     if propToUpdt in ['updt_producto_codigo','codeChanged']:continue
     print('-------------->',propToUpdt)
     dictRepr[propToUpdt]=req.data['payload'][propToUpdt]
    #  recordToUpdt.update(**{propToUpdt:req.data['payload'][propToUpdt]})
    #  if recordToUpdt:M.Producto.objects.filter(Codigo=req.data['payload']['updt_producto_codigo']).update(**{propToUpdt:req.data['payload'][propToUpdt]})
    if recordToUpdt:recordToUpdt.update(**dictRepr)
   elif 'Codigo' in req.data['payload']:
    codeToLook = req.data['payload']['Codigo'] 
    foundRecord = list(M.Producto.objects.filter(Codigo=codeToLook))
    if foundRecord:return Response({'msg':'El código %s esta siendo usado por el producto: %s'%(codeToLook,foundRecord[0].Descripcion)})    

    M.Producto.objects.create(**req.data['payload'])
  if req.data['mode'] == 'save_ficha_tecnica':
   productCodigo = req.data['productCode']
   recordToUpdate = list(M.Producto.objects.filter(Codigo=productCodigo))
   if recordToUpdate and type(req.data['file']) != str:
    recordToUpdate[0].FichaTecnica = req.data['file'].read()
    recordToUpdate[0].save()   
  if req.data['mode'] == 'request_ficha_tecnica':
   productCodigo = req.data['productCode'].split('_')[1].replace(' ','').strip()
   procedRecord = list(M.Producto.objects.filter(Codigo=productCodigo))
   if procedRecord:
     file = bytes(procedRecord[0].FichaTecnica)
     mime = magic.Magic(mime=True)
     tipo_mime = mime.from_buffer(file)    
     return HttpResponse(file,content_type=tipo_mime)
   return Response([]) 
  if req.data['mode'] == 'reqSeqCode':
   if req.data['payload']:
    seqToSearch = M.Clase.objects.filter(pk=req.data['payload']).values('Codigo')
    if seqToSearch:
     newSeq = False
     seqToSearch = seqToSearch[0]['Codigo']
     highestSequence = list(M.Producto.objects.filter(Codigo__contains=seqToSearch).order_by('Codigo'))
     if highestSequence:
      highestSequence = highestSequence[-1].Codigo
      incrementedNumber = str(int(highestSequence[-2:]) + 1)
      newSeq = str(seqToSearch) + incrementedNumber.zfill(2)
     else:
      newSeq = str(seqToSearch) + '01'
     return Response({'seq':newSeq})
   return Response([])
  if req.data['mode'] == 'generateProductRecords':
   host = 'localhost'
   dbname = 'maestromateriales'
   user = 'postgres'
   password = 'seguridad2023'
   conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password)
  #  query = 'WITH UM AS (SELECT "ID","Descripcion" FROM "UnidadMedida") SELECT "Codigo","Descripcion",UM.Descripcion,"Categoria","EstadoMaterial","Minimo","Maximo","PuntoReorden","Proveedor","TiempoEntrega","PedidoEstandar","LoteMinimo","LoteMaximo","TiempoProcesoInterno","TiempoVidaUtil" FROM "Producto"'
   query = 'WITH "UM" AS (SELECT "ID","Descripcion" FROM "UnidadMedida"),' \
   '"CAT" AS (SELECT "ID","Descripcion" FROM "Categoria"),' \
   '"EST" AS (SELECT "ID","Descripcion" FROM "EstadoMaterial")' \
   ',"PROV" AS (SELECT "ID","Descripcion" FROM "Proveedor")'\
   'SELECT "Codigo","Descripcion",(SELECT "Descripcion" FROM "UM" WHERE "ID"="UnidadMedida") AS "UnidadMedida",' \
   '(SELECT "Descripcion" FROM "CAT" WHERE "ID"="Categoria") AS "Categoria",' \
   '(SELECT "Descripcion" FROM "EST" WHERE "ID"="EstadoMaterial") AS "EstadoMaterial",' \
   '"Minimo","Maximo","PuntoReorden",' \
   '(SELECT "Descripcion" FROM "PROV" WHERE "ID"="Proveedor") AS "Proveedor",' \
   '"TiempoEntrega","PedidoEstandar","LoteMinimo","LoteMaximo","TiempoProcesoInterno","TiempoVidaUtil" FROM "Producto"'
   df = pd.read_sql(query, conn)   
   df.to_excel('lista_productos.xlsx', index=False, engine='openpyxl')
   conn.close()
   if os.path.exists('lista_productos.xlsx'):
    with open('lista_productos.xlsx', 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="lista_productos.xlsx"'
            return response
   return Response({'msg':'False'})
  if req.data['mode'] == 'reqCodeAllSeqData':  
  #  deprec
   seqToSearch = M.Clase.objects.filter(pk=req.data['payload']).values('Codigo')
   if seqToSearch: 
    seqToSearch = seqToSearch[0]['Codigo']
    productRecords = M.Producto.objects.filter(Codigo__contains=seqToSearch).values('ID','Descripcion')
    print('------------>',productRecords)
   return Response(productRecords)   

  if req.data['mode'] == 'delete':
   recordToDeleteCode = req.data['code'].replace(' ','').strip()
   record = M.Producto.objects.filter(Codigo=recordToDeleteCode)
   if record:record[0].delete()

  return Response({'msg':'ok'})
 
 def delete(self,req):
  return Response({})
 
 def retrieve(self,req):
  return Response({})
 
 def list(self, req):
  data = {'columns':[{'title':'Codigo'},{'title':'Descripcion'},{'title':'UnidadMedida'},{'title':'Categoria'},{'title':'EstadoMaterial'},{'title':'Minimo'},{'title':'Maximo'},{'title':'PuntoReorden'},{'title':'Proveedor'},{'title':'TiempoEntrega'},{'title':'PedidoEstandar'},{'title':'LoteMinimo'},{'title':'LoteMaximo'},{'title':'TiempoProcesoInterno'},{'title':'TiempoVidaUtil'}],'records':[]}
  recordsList = M.Producto.objects.all().values('Codigo','Descripcion','UnidadMedida','Categoria','EstadoMaterial','Minimo','Maximo','PuntoReorden','Proveedor','TiempoEntrega','PedidoEstandar','LoteMinimo','LoteMaximo','TiempoProcesoInterno','TiempoVidaUtil')
  for record in recordsList.values():
   parsedRecord = {**record}
   del parsedRecord['ID']
   del parsedRecord['FichaTecnica']
   del parsedRecord['Codigo_repr']
   del parsedRecord['Clase']
   unidadMedida = M.UnidadMedida.objects.filter(pk=parsedRecord['UnidadMedida']).values('Descripcion')
   categoria = M.Categoria.objects.filter(pk=parsedRecord['Categoria']).values('Descripcion')
   estadoMaterial = M.EstadoMaterial.objects.filter(pk=parsedRecord['EstadoMaterial']).values('Descripcion')
   proveedor = M.Proveedor.objects.filter(pk=parsedRecord['Proveedor']).values('Descripcion')

   parsedRecord['UnidadMedida'] = unidadMedida[0]['Descripcion'] if unidadMedida else ''
   parsedRecord['Categoria'] = categoria[0]['Descripcion'] if categoria else ''
   parsedRecord['EstadoMaterial'] = estadoMaterial[0]['Descripcion'] if estadoMaterial else ''
   parsedRecord['Proveedor'] = proveedor[0]['Descripcion'] if proveedor else ''
   data['records'].append(list(parsedRecord.values()))
  return Response(data)


class UsuarioView(viewsets.ViewSet):
 
 def create(self,req):
  user = req.data['cred']['username']
  password = req.data['cred']['password']
  if req.data['mode'] == 'userCreation':
   permisonivel = req.data['cred']['permisonivel']
   readyPass = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
   M.Usuario.objects.create(**{'Nombre':user,'Contrasena':readyPass,'Activo':True,'PermisoNivel':permisonivel})
   return Response({'msg':'ok'})   
  elif req.data['mode'] == 'login': 
   recordsToFilter = list(M.Usuario.objects.filter(Nombre=user))
   for record in recordsToFilter:
    hashedPass = record.Contrasena.tobytes()
    if bcrypt.checkpw(password.encode('utf-8'),hashedPass):return Response({'Nombre':record.Nombre,'Activo':record.Activo,'PermisoNivel':record.PermisoNivel,'msg':'ok'})
  return Response([])


class CategoriaView(viewsets.ViewSet):
 
 def create(self,req):  

  if req.data['mode'] == 'create':

   payload = req.data['payload']
   payload = {'Descripcion':payload}
   createdObj = M.Categoria.objects.create(**payload)
   return Response({'msg':'ok','ID':createdObj.pk,'Descripcion':createdObj.Descripcion})
  elif req.data['mode'] == 'fillForm':  
   specificRecord = M.Categoria.objects.filter(Descripcion=req.data['code'].replace('updt_','').strip())
   if specificRecord:return Response(specificRecord.values('ID','Descripcion'))
  elif req.data['mode'] == 'update':
   M.Categoria.objects.filter(Descripcion=req.data['recordCode'].replace('updt_','').strip()).update(**{'Descripcion':req.data['payload']})
  if req.data['mode'] == 'delete':
   recordToDeleteCode = req.data['code'].replace(' ','').strip()
   record = M.Categoria.objects.filter(Descripcion=recordToDeleteCode)
   if record:record[0].delete() 

  return Response({'msg':'ok'}) 
 
 def delete(self,req):
  return Response({})
 
 def retrieve(self,req):
  return Response({})
 
 def list(self, req):
  data = {'columns':[{'title':'Descripción'}],'records':[]}
  recordList = M.Categoria.objects.all().values('Descripcion')
  for record in recordList:data['records'].append(list(record.values()))

  return Response(data)


class UnidadMedidaView(viewsets.ViewSet):
 
 def create(self,req):
  if req.data['mode'] == 'create':
   payload = req.data['payload']
   payload = {'Descripcion':payload}
   createdObj = M.UnidadMedida.objects.create(**payload)
   return Response({'msg':'ok','ID':createdObj.pk,'Descripcion':createdObj.Descripcion})
  elif req.data['mode'] == 'fillForm':  
   specificRecord = M.UnidadMedida.objects.filter(Descripcion=req.data['code'].replace('updt_','').strip())
   if specificRecord:return Response(specificRecord.values('ID','Descripcion'))
  elif req.data['mode'] == 'update':
   M.UnidadMedida.objects.filter(Descripcion=req.data['recordCode'].replace('updt_','').strip()).update(**{'Descripcion':req.data['payload']})
  if req.data['mode'] == 'delete':
   recordToDeleteCode = req.data['code'].replace(' ','').strip()
   record = M.UnidadMedida.objects.filter(Descripcion=recordToDeleteCode)
   if record:record[0].delete()  

  return Response({'msg':'ok'})
 
 def delete(self,req):
  return Response({})
 
 def retrieve(self,req):
  return Response({})
 
 def list(self, req):
  data = {'columns':[{'title':'Descripción'}],'records':[]}
  recordList = M.UnidadMedida.objects.all().values('Descripcion')
  for record in recordList:data['records'].append(list(record.values()))

  return Response(data)


class EstadoMaterialView(viewsets.ViewSet):
 
 def create(self,req):
  if req.data['mode'] == 'create':
   payload = req.data['payload']
   payload = {'Descripcion':payload}
   createdObj = M.EstadoMaterial.objects.create(**payload)
   return Response({'msg':'ok','ID':createdObj.pk,'Descripcion':createdObj.Descripcion})
  elif req.data['mode'] == 'fillForm':  
   specificRecord = M.EstadoMaterial.objects.filter(Descripcion=req.data['code'].replace('updt_','').strip())
   if specificRecord:return Response(specificRecord.values('ID','Descripcion'))
  elif req.data['mode'] == 'update':
   M.EstadoMaterial.objects.filter(Descripcion=req.data['recordCode'].replace('updt_','').strip()).update(**{'Descripcion':req.data['payload']})
  if req.data['mode'] == 'delete':
   recordToDeleteCode = req.data['code'].replace(' ','').strip()
   record = M.EstadoMaterial.objects.filter(Descripcion=recordToDeleteCode)
   if record:record[0].delete()  

  return Response({'msg':'ok'})
 
 def delete(self,req):
  return Response({})
 
 def retrieve(self,req):
  return Response({})
 
 def list(self, req):
  data = {'columns':[{'title':'Descripción'}],'records':[]}
  recordList = M.EstadoMaterial.objects.all().values('Descripcion')
  for record in recordList:data['records'].append(list(record.values()))

  return Response(data)
 

class ProveedorView(viewsets.ViewSet):
 
 def create(self,req):
  if req.data['mode'] == 'create':
   payload = req.data['payload']
   payload = {'Descripcion':payload}
   createdObj = M.Proveedor.objects.create(**payload)
   return Response({'msg':'ok','ID':createdObj.pk,'Descripcion':createdObj.Descripcion})
  elif req.data['mode'] == 'fillForm':  
   specificRecord = M.Proveedor.objects.filter(Descripcion=req.data['code'].replace('updt_','').strip())
   if specificRecord:return Response(specificRecord.values('ID','Descripcion'))
  elif req.data['mode'] == 'update':
   M.Proveedor.objects.filter(Descripcion=req.data['recordCode'].replace('updt_','').strip()).update(**{'Descripcion':req.data['payload']})
  if req.data['mode'] == 'delete':
   recordToDeleteCode = req.data['code'].replace(' ','').strip()
   record = M.Proveedor.objects.filter(Descripcion=recordToDeleteCode)
   if record:record[0].delete()  

  return Response({'msg':'ok'})
 
 def delete(self,req):
  return Response({})
 
 def retrieve(self,req):
  return Response({})
 
 def list(self, req):
  data = {'columns':[{'title':'Descripción'}],'records':[]}
  recordList = M.Proveedor.objects.all().values('Descripcion')
  for record in recordList:data['records'].append(list(record.values()))

  return Response(data)

class FamiliaView(viewsets.ViewSet):
 
 def list(self,req):
  records = M.Familia.objects.all().values('ID','Descripcion')
  return Response(records)

 def create(self,req):
  if req.data['mode'] == 'listFilteredRecords':
   if req.data['payload']:
    segmentoRecord = M.Segmento.objects.filter(pk=req.data['payload']).values('Codigo')
    if segmentoRecord:
     segmentoRecord = segmentoRecord[0]
     familiaRecords = M.Familia.objects.filter(Segmento=segmentoRecord['Codigo']).values('ID','Descripcion','Codigo')
     return Response(familiaRecords)  
  if req.data['mode'] == 'reqCodeAllSeqData':  
   data = {'columns':[{'title':'Codigo'},{'title':'Descripcion'},{'title':'UnidadMedida'},{'title':'Categoria'},{'title':'EstadoMaterial'},{'title':'Minimo'},{'title':'Maximo'},{'title':'PuntoReorden'},{'title':'Proveedor'},{'title':'TiempoEntrega'},{'title':'PedidoEstandar'},{'title':'LoteMinimo'},{'title':'LoteMaximo'},{'title':'TiempoProcesoInterno'},{'title':'TiempoVidaUtil'}],'records':[]}
   familiaCodigo = M.Familia.objects.filter(pk=req.data['payload']).values('Codigo')
   if familiaCodigo:
    familiaCodigo = familiaCodigo[0]['Codigo']
    # familiaSegmentos = M.Segmento.objects.filter(Familia=familiaCodigo).values('Codigo')
    # for segmentoCode in familiaSegmentos:
    #  segmentoCode = segmentoCode['Codigo']
    clasesCodigo = M.Clase.objects.filter(Familia=familiaCodigo).values('Codigo')
    for seqToLook in clasesCodigo:
      productoRecords = M.Producto.objects.filter(Codigo__contains=seqToLook['Codigo']).values('Codigo','Descripcion','UnidadMedida','Categoria','EstadoMaterial','Minimo','Maximo','PuntoReorden','Proveedor','TiempoEntrega','PedidoEstandar','LoteMinimo','LoteMaximo','TiempoProcesoInterno','TiempoVidaUtil')
     
      for record in productoRecords.values():
        parsedRecord = {**record}
        del parsedRecord['ID']
        del parsedRecord['FichaTecnica']
        del parsedRecord['Codigo_repr']
        del parsedRecord['Clase']
        unidadMedida = M.UnidadMedida.objects.filter(pk=parsedRecord['UnidadMedida']).values('Descripcion')
        categoria = M.Categoria.objects.filter(pk=parsedRecord['Categoria']).values('Descripcion')
        estadoMaterial = M.EstadoMaterial.objects.filter(pk=parsedRecord['EstadoMaterial']).values('Descripcion')
        proveedor = M.Proveedor.objects.filter(pk=parsedRecord['Proveedor']).values('Descripcion')

        parsedRecord['UnidadMedida'] = unidadMedida[0]['Descripcion'] if unidadMedida else ''
        parsedRecord['Categoria'] = categoria[0]['Descripcion'] if categoria else ''
        parsedRecord['EstadoMaterial'] = estadoMaterial[0]['Descripcion'] if estadoMaterial else ''
        parsedRecord['Proveedor'] = proveedor[0]['Descripcion'] if proveedor else ''
        data['records'].append(list(parsedRecord.values()))
   return Response(data) 
  return Response([])
 
class SegmentoView(viewsets.ViewSet):
 
 def list(self,req):
  records = M.Segmento.objects.all().values('ID','Descripcion','Codigo')
  return Response(records)   

 def create(self,req):
  if req.data['mode'] == 'reqCodeAllSeqData':  
   data = {'columns':[{'title':'Codigo'},{'title':'Descripcion'},{'title':'UnidadMedida'},{'title':'Categoria'},{'title':'EstadoMaterial'},{'title':'Minimo'},{'title':'Maximo'},{'title':'PuntoReorden'},{'title':'Proveedor'},{'title':'TiempoEntrega'},{'title':'PedidoEstandar'},{'title':'LoteMinimo'},{'title':'LoteMaximo'},{'title':'TiempoProcesoInterno'},{'title':'TiempoVidaUtil'}],'records':[]}
   segmentoCode = M.Segmento.objects.filter(pk=req.data['payload']).values('Codigo')
   if segmentoCode:
    segmentoCode = segmentoCode[0]['Codigo']
    segmentoFamilias = M.Familia.objects.filter(Segmento=segmentoCode).values('Codigo')
    for familiasCode in segmentoFamilias:
     familiaCode = familiasCode['Codigo']    
     clasesCodigo = M.Clase.objects.filter(Familia=familiaCode).values('Codigo')
     for seqToLook in clasesCodigo:
      productoRecords = M.Producto.objects.filter(Codigo__contains=seqToLook['Codigo']).values('Codigo','Descripcion','UnidadMedida','Categoria','EstadoMaterial','Minimo','Maximo','PuntoReorden','Proveedor','TiempoEntrega','PedidoEstandar','LoteMinimo','LoteMaximo','TiempoProcesoInterno','TiempoVidaUtil')
     
      for record in productoRecords.values():
        parsedRecord = {**record}
        del parsedRecord['ID']
        del parsedRecord['FichaTecnica']
        del parsedRecord['Codigo_repr']
        del parsedRecord['Clase']
        unidadMedida = M.UnidadMedida.objects.filter(pk=parsedRecord['UnidadMedida']).values('Descripcion')
        categoria = M.Categoria.objects.filter(pk=parsedRecord['Categoria']).values('Descripcion')
        estadoMaterial = M.EstadoMaterial.objects.filter(pk=parsedRecord['EstadoMaterial']).values('Descripcion')
        proveedor = M.Proveedor.objects.filter(pk=parsedRecord['Proveedor']).values('Descripcion')

        parsedRecord['UnidadMedida'] = unidadMedida[0]['Descripcion'] if unidadMedida else ''
        parsedRecord['Categoria'] = categoria[0]['Descripcion'] if categoria else ''
        parsedRecord['EstadoMaterial'] = estadoMaterial[0]['Descripcion'] if estadoMaterial else ''
        parsedRecord['Proveedor'] = proveedor[0]['Descripcion'] if proveedor else ''
        data['records'].append(list(parsedRecord.values()))
   return Response(data)
  return Response({})
  
class ClaseView(viewsets.ViewSet):
 
 def list(self,req):
  records = M.Clase.objects.all().values('ID','Descripcion')
  return Response(records) 

 def create(self,req):
  if req.data['mode'] == 'listFilteredRecords':
   if req.data['payload']:
    familiaRecord = M.Familia.objects.filter(pk=req.data['payload']).values('Codigo')
    if familiaRecord:
     familiaRecord = familiaRecord[0]
     claseRecords = M.Clase.objects.filter(Familia=familiaRecord['Codigo']).values('ID','Descripcion','Codigo')
     return Response(claseRecords)
  if req.data['mode'] == 'reqCodeAllSeqData':  
   data = {'columns':[{'title':'Codigo'},{'title':'Descripcion'},{'title':'UnidadMedida'},{'title':'Categoria'},{'title':'EstadoMaterial'},{'title':'Minimo'},{'title':'Maximo'},{'title':'PuntoReorden'},{'title':'Proveedor'},{'title':'TiempoEntrega'},{'title':'PedidoEstandar'},{'title':'LoteMinimo'},{'title':'LoteMaximo'},{'title':'TiempoProcesoInterno'},{'title':'TiempoVidaUtil'}],'records':[]}
   clasesCodigo = M.Clase.objects.filter(pk=req.data['payload']).values('Codigo')
   print('---------------->',clasesCodigo)
   if clasesCodigo:
     clasesCodigo = clasesCodigo[0]['Codigo']
     productoRecords = M.Producto.objects.filter(Codigo__contains=clasesCodigo).values('Codigo','Descripcion','UnidadMedida','Categoria','EstadoMaterial','Minimo','Maximo','PuntoReorden','Proveedor','TiempoEntrega','PedidoEstandar','LoteMinimo','LoteMaximo','TiempoProcesoInterno','TiempoVidaUtil')
     
     for record in productoRecords.values():
        parsedRecord = {**record}
        del parsedRecord['ID']
        del parsedRecord['FichaTecnica']
        del parsedRecord['Codigo_repr']
        del parsedRecord['Clase']
        unidadMedida = M.UnidadMedida.objects.filter(pk=parsedRecord['UnidadMedida']).values('Descripcion')
        categoria = M.Categoria.objects.filter(pk=parsedRecord['Categoria']).values('Descripcion')
        estadoMaterial = M.EstadoMaterial.objects.filter(pk=parsedRecord['EstadoMaterial']).values('Descripcion')
        proveedor = M.Proveedor.objects.filter(pk=parsedRecord['Proveedor']).values('Descripcion')

        parsedRecord['UnidadMedida'] = unidadMedida[0]['Descripcion'] if unidadMedida else ''
        parsedRecord['Categoria'] = categoria[0]['Descripcion'] if categoria else ''
        parsedRecord['EstadoMaterial'] = estadoMaterial[0]['Descripcion'] if estadoMaterial else ''
        parsedRecord['Proveedor'] = proveedor[0]['Descripcion'] if proveedor else ''
        data['records'].append(list(parsedRecord.values()))
   return Response(data)
  return Response({})  


router = DefaultRouter()
router.register(r'producto', ProductoView, basename='producto')
router.register(r'usuario', UsuarioView, basename='usuario')
router.register(r'categoria', CategoriaView, basename='categoria')
router.register(r'unidadmedida', UnidadMedidaView, basename='unidadmedida')
router.register(r'estadomaterial', EstadoMaterialView, basename='estadomaterial')
router.register(r'proveedor', ProveedorView, basename='proveedor')
router.register(r'familia', FamiliaView, basename='familia')
router.register(r'segmento', SegmentoView, basename='segmento')
router.register(r'clase', ClaseView, basename='clase')

urlpatterns = router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
