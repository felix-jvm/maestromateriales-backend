from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from django.conf.urls.static import static
from django.http import HttpResponse
from rest_framework import viewsets
from django.conf import settings
from django.contrib import admin
from django.urls import path
import api.models as M
import bcrypt
import json

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
   if procedRecord:return HttpResponse(procedRecord[0].FichaTecnica,content_type='image/png')
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
   
   M.Segmento.objects.create(**{'Codigo':'10', 'Descripcion':'Productos agrícolas, alimentos y bebidas'})
   M.Segmento.objects.create(**{'Codigo':'11', 'Descripcion':'Productos textiles, prendas de vestir y accesorios'})
   M.Segmento.objects.create(**{'Codigo':'12', 'Descripcion':'Productos y servicios químicos'})
   M.Segmento.objects.create(**{'Codigo':'14', 'Descripcion':'Equipos de oficina, papelería y material escolar'})
   M.Segmento.objects.create(**{'Codigo':'18', 'Descripcion':'Servicios profesionales'})


   M.Familia.objects.create(**{'Codigo':'1001', 'Descripcion':'Frutas y verduras', 'Segmento':'10'})
   M.Familia.objects.create(**{'Codigo':'1002', 'Descripcion':'Bebidas no alcohólicas', 'Segmento':'10'})

   M.Familia.objects.create(**{'Codigo':'1101', 'Descripcion':'Ropa masculina', 'Segmento':'11'})
   M.Familia.objects.create(**{'Codigo':'1102', 'Descripcion':'Accesorios de moda', 'Segmento':'11'})

   M.Familia.objects.create(**{'Codigo':'1201', 'Descripcion':'Productos de limpieza', 'Segmento':'12'})
   M.Familia.objects.create(**{'Codigo':'1202', 'Descripcion':'Productos farmacéuticos', 'Segmento':'12'})

   M.Familia.objects.create(**{'Codigo':'1401', 'Descripcion':'Mobiliario de oficina', 'Segmento':'14'})
   M.Familia.objects.create(**{'Codigo':'1402', 'Descripcion':'Material de oficina', 'Segmento':'14'})

   M.Familia.objects.create(**{'Codigo':'1801', 'Descripcion':'Consultoría empresarial', 'Segmento':'18'})
   M.Familia.objects.create(**{'Codigo':'1802', 'Descripcion':'Servicios legales', 'Segmento':'18'})


   M.Clase.objects.create(**{'Codigo':'100101', 'Descripcion':'Frutas frescas', 'Familia':'1001'})
   M.Clase.objects.create(**{'Codigo':'100102', 'Descripcion':'Verduras frescas', 'Familia':'1001'})

   M.Clase.objects.create(**{'Codigo':'100201', 'Descripcion':'Jugos naturales', 'Familia':'1002'})
   M.Clase.objects.create(**{'Codigo':'100202', 'Descripcion':'Agua embotellada', 'Familia':'1002'})

   M.Clase.objects.create(**{'Codigo':'110101', 'Descripcion':'Camisas', 'Familia':'1101'})
   M.Clase.objects.create(**{'Codigo':'110102', 'Descripcion':'Pantalones', 'Familia':'1101'})

   M.Clase.objects.create(**{'Codigo':'110201', 'Descripcion':'Bolsos y carteras', 'Familia':'1102'})
   M.Clase.objects.create(**{'Codigo':'110202', 'Descripcion':'Gafas de sol', 'Familia':'1102'})

   M.Clase.objects.create(**{'Codigo':'120101', 'Descripcion':'Detergentes', 'Familia':'1201'})
   M.Clase.objects.create(**{'Codigo':'120102', 'Descripcion':'Limpiadores multiusos', 'Familia':'1201'})

   M.Clase.objects.create(**{'Codigo':'120201', 'Descripcion':'Medicamentos para el dolor', 'Familia':'1202'})
   M.Clase.objects.create(**{'Codigo':'120202', 'Descripcion':'Vitaminas y suplementos', 'Familia':'1202'})

   M.Clase.objects.create(**{'Codigo':'140101', 'Descripcion':'Escritorios', 'Familia':'1401'})
   M.Clase.objects.create(**{'Codigo':'140102', 'Descripcion':'Sillas de oficina', 'Familia':'1401'})

   M.Clase.objects.create(**{'Codigo':'140201', 'Descripcion':'Papelería', 'Familia':'1402'})
   M.Clase.objects.create(**{'Codigo':'140202', 'Descripcion':'Lentes y proyectores', 'Familia':'1402'})

   M.Clase.objects.create(**{'Codigo':'180101', 'Descripcion':'Consultoría financiera', 'Familia':'1801'})
   M.Clase.objects.create(**{'Codigo':'180102', 'Descripcion':'Consultoría en recursos humanos', 'Familia':'1801'})

   M.Clase.objects.create(**{'Codigo':'180201', 'Descripcion':'Asesoría legal corporativa', 'Familia':'1802'})
   M.Clase.objects.create(**{'Codigo':'180202', 'Descripcion':'Litigios y demandas', 'Familia':'1802'})

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
     familiaRecords = M.Familia.objects.filter(Segmento=segmentoRecord['Codigo']).values('ID','Descripcion')
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
  records = M.Segmento.objects.all().values('ID','Descripcion')
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
     claseRecords = M.Clase.objects.filter(Familia=familiaRecord['Codigo']).values('ID','Descripcion')
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
