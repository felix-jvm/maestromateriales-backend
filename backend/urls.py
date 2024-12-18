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
    if 'codeChanged' in req.data['payload'].keys() and req.data['payload']['codeChanged']:
     codeToLook = req.data['payload']['Codigo']
     foundRecord = list(M.Producto.objects.filter(Codigo=codeToLook))
     if foundRecord:return Response({'msg':'El código %s esta siendo usado por el producto: %s'%(codeToLook,foundRecord[0].Descripcion)})

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

  M.Familia.objects.create(**{'Codigo':'10','Descripcion':'Bienes y servicios generales'})
  M.Familia.objects.create(**{'Codigo':'11','Descripcion':'Materiales y suministros de oficina'})
  M.Familia.objects.create(**{'Codigo':'15','Descripcion':'Servicios profesionales'})
  M.Familia.objects.create(**{'Codigo':'30','Descripcion':'Construcción, minería, energía y productos relacionados'})
  M.Familia.objects.create(**{'Codigo':'41','Descripcion':'Tecnologías de la información y servicios relacionados'})
  M.Familia.objects.create(**{'Codigo':'60','Descripcion':'Servicios de transporte y almacenaje'})
  M.Familia.objects.create(**{'Codigo':'72','Descripcion':'Productos químicos y productos derivados'})
  M.Familia.objects.create(**{'Codigo':'73','Descripcion':'Equipos y suministros de comunicaciones'})
  M.Familia.objects.create(**{'Codigo':'76','Descripcion':'Servicios de educación y capacitación'})
  M.Familia.objects.create(**{'Codigo':'82','Descripcion':'Servicios financieros y seguros'})


  M.Segmento.objects.create(**{'Codigo':'1001','Descripcion':'Productos y servicios generales','Familia':'10'})
  M.Segmento.objects.create(**{'Codigo':'1002','Descripcion':'Materiales para oficina','Familia':'10'})
  M.Segmento.objects.create(**{'Codigo':'1003','Descripcion':'Servicios generales','Familia':'10'})

  M.Segmento.objects.create(**{'Codigo':'1101','Descripcion':'Mobiliario de oficina','Familia':'11'})
  M.Segmento.objects.create(**{'Codigo':'1102','Descripcion':'Material de oficina','Familia':'11'})
  M.Segmento.objects.create(**{'Codigo':'1103','Descripcion':'Equipo de oficina','Familia':'11'}) 

  M.Segmento.objects.create(**{'Codigo':'1501','Descripcion':'Consultoría y asesoría','Familia':'15'})
  M.Segmento.objects.create(**{'Codigo':'1502','Descripcion':'Servicios jurídicos','Familia':'15'})
  M.Segmento.objects.create(**{'Codigo':'1503','Descripcion':'Servicios de marketing y publicidad','Familia':'15'})

  M.Segmento.objects.create(**{'Codigo':'3001','Descripcion':'Materiales para la construcción','Familia':'30'})
  M.Segmento.objects.create(**{'Codigo':'3002','Descripcion':'Equipo de minería','Familia':'30'})
  M.Segmento.objects.create(**{'Codigo':'3003','Descripcion':'Servicios de energía y recursos naturales','Familia':'30'})

  M.Segmento.objects.create(**{'Codigo':'4101','Descripcion':'Equipos informáticos','Familia':'41'})
  M.Segmento.objects.create(**{'Codigo':'4102','Descripcion':'Software y aplicaciones','Familia':'41'})
  M.Segmento.objects.create(**{'Codigo':'4103','Descripcion':'Servicios de soporte informático','Familia':'41'})

  M.Segmento.objects.create(**{'Codigo':'6001','Descripcion':'Transporte de carga','Familia':'60'})
  M.Segmento.objects.create(**{'Codigo':'6002','Descripcion':'Servicios de almacenamiento','Familia':'60'})
  M.Segmento.objects.create(**{'Codigo':'6003','Descripcion':'Transporte de pasajeros','Familia':'60'})  

  M.Segmento.objects.create(**{'Codigo':'7201','Descripcion':'Productos químicos generales','Familia':'72'})
  M.Segmento.objects.create(**{'Codigo':'7202','Descripcion':'Productos farmacéuticos','Familia':'72'})
  M.Segmento.objects.create(**{'Codigo':'7203','Descripcion':'Productos químicos especializados','Familia':'72'})

  M.Segmento.objects.create(**{'Codigo':'7301','Descripcion':'Equipos de telecomunicaciones','Familia':'73'})
  M.Segmento.objects.create(**{'Codigo':'7302','Descripcion':'Suministros para comunicaciones','Familia':'73'})
  M.Segmento.objects.create(**{'Codigo':'7303','Descripcion':'Servicios de comunicaciones','Familia':'73'})  

  M.Segmento.objects.create(**{'Codigo':'7601','Descripcion':'Servicios educativos','Familia':'76'})
  M.Segmento.objects.create(**{'Codigo':'7602','Descripcion':'Servicios de formación profesional','Familia':'76'})
  M.Segmento.objects.create(**{'Codigo':'7603','Descripcion':'Servicios de capacitación corporativa','Familia':'76'})  

  M.Segmento.objects.create(**{'Codigo':'8201','Descripcion':'Servicios bancarios','Familia':'82'})
  M.Segmento.objects.create(**{'Codigo':'8202','Descripcion':'Seguros y pensiones','Familia':'82'})
  M.Segmento.objects.create(**{'Codigo':'8203','Descripcion':'Servicios de asesoría financiera','Familia':'82'})  



  M.Clase.objects.create(**{'Codigo':'100101','Descripcion':'Productos diversos para consumo general','Segmento':'1001'})
  M.Clase.objects.create(**{'Codigo':'100102','Descripcion':'Servicios generales de uso común','Segmento':'1001'})

  M.Clase.objects.create(**{'Codigo':'100201','Descripcion':'Papelería y artículos de oficina','Segmento':'1002'})
  M.Clase.objects.create(**{'Codigo':'100202','Descripcion':'Suministros y material de oficina','Segmento':'1002'})

  M.Clase.objects.create(**{'Codigo':'100301','Descripcion':'Servicios de limpieza y mantenimiento generales','Segmento':'1003'})
  M.Clase.objects.create(**{'Codigo':'100302','Descripcion':'Servicios generales de reparación','Segmento':'1003'})  

  M.Clase.objects.create(**{'Codigo':'110101','Descripcion':'Escritorios y mesas de oficina','Segmento':'1101'})
  M.Clase.objects.create(**{'Codigo':'110102','Descripcion':'Sillas y asientos para oficina','Segmento':'1101'})

  M.Clase.objects.create(**{'Codigo':'110201','Descripcion':'Papelería, bolígrafos y artículos de escritura','Segmento':'1102'})
  M.Clase.objects.create(**{'Codigo':'110202','Descripcion':'Material para impresión y copiado','Segmento':'1102'})  

  M.Clase.objects.create(**{'Codigo':'110301','Descripcion':'Fotocopiadoras y escáneres','Segmento':'1103'})
  M.Clase.objects.create(**{'Codigo':'110302','Descripcion':'Equipos de computación para oficina','Segmento':'1103'})

  M.Clase.objects.create(**{'Codigo':'150101','Descripcion':'Consultoría en gestión empresarial','Segmento':'1501'})
  M.Clase.objects.create(**{'Codigo':'150102','Descripcion':'Consultoría en tecnología de la información','Segmento':'1501'})  

  M.Clase.objects.create(**{'Codigo':'150201','Descripcion':'Asesoría legal en derechos civiles','Segmento':'1502'})
  M.Clase.objects.create(**{'Codigo':'150202','Descripcion':'Servicios legales corporativos','Segmento':'1502'})  

  M.Clase.objects.create(**{'Codigo':'150301','Descripcion':'Publicidad en medios digitales','Segmento':'1503'})
  M.Clase.objects.create(**{'Codigo':'150302','Descripcion':'Estrategias de marketing y branding','Segmento':'1503'})  

  M.Clase.objects.create(**{'Codigo':'300101','Descripcion':'Cemento y derivados','Segmento':'3001'})
  M.Clase.objects.create(**{'Codigo':'300102','Descripcion':'Acero y materiales metálicos para construcción','Segmento':'3001'})  

  M.Clase.objects.create(**{'Codigo':'300201','Descripcion':'Maquinaria pesada para minería','Segmento':'3002'})
  M.Clase.objects.create(**{'Codigo':'300202','Descripcion':'Herramientas y equipos para minería subterránea','Segmento':'3002'})  

  M.Clase.objects.create(**{'Codigo':'300301','Descripcion':'Servicios de extracción de petróleo y gas','Segmento':'3003'})
  M.Clase.objects.create(**{'Codigo':'300302','Descripcion':'Suministro de energía eléctrica y gas natural','Segmento':'3003'})  

  M.Clase.objects.create(**{'Codigo':'410101','Descripcion':'Computadoras de escritorio y portátiles','Segmento':'4101'})
  M.Clase.objects.create(**{'Codigo':'410102','Descripcion':'Servidores y equipos de almacenamiento','Segmento':'4101'})  

  M.Clase.objects.create(**{'Codigo':'410201','Descripcion':'Software de productividad','Segmento':'4102'})
  M.Clase.objects.create(**{'Codigo':'410202','Descripcion':'Aplicaciones empresariales y CRM','Segmento':'4102'})  

  M.Clase.objects.create(**{'Codigo':'410301','Descripcion':'Servicios de mantenimiento de software','Segmento':'4103'})
  M.Clase.objects.create(**{'Codigo':'410302','Descripcion':'Soporte técnico y servicio al cliente','Segmento':'4103'})  


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
  records = M.Familia.objects.values('ID','Descripcion')
  return Response(records)

class SegmentoView(viewsets.ViewSet):
 
 def create(self,req):
  if req.data['mode'] == 'listFilteredRecords':
   if req.data['payload']:
    familiaRecord = M.Familia.objects.filter(pk=req.data['payload']).values('Codigo')
    if familiaRecord:
     familiaRecord = familiaRecord[0]
     segmentoRecords = M.Segmento.objects.filter(Familia=familiaRecord['Codigo']).values('ID','Descripcion')
     return Response(segmentoRecords)
  return Response({})
  
class ClaseView(viewsets.ViewSet):
 
 def list(self,req):
  pass
 
 def create(self,req):
  if req.data['mode'] == 'listFilteredRecords':
   if req.data['payload']:
    segmentoRecord = M.Segmento.objects.filter(pk=req.data['payload']).values('Codigo','Familia')
    if segmentoRecord:
     segmentoRecord = segmentoRecord[0]
     claseRecords = M.Clase.objects.filter(Segmento=segmentoRecord['Codigo']).values('ID','Descripcion')
     print('---------------->',claseRecords)
     return Response(claseRecords)
  return Response([])  


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
