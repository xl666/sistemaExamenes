
from django.shortcuts import render_to_response
from examenesEscritos.decoradores import *
from modelo import models
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.shortcuts import redirect
import xml.examen
import xml.subrayar
from examenesEscritos import settings
import datetime
import socket



@examenActivo
def login(request):
    # asegurarse de que hay sesion
    if not request.session.session_key:
        request.session.create()

    # ya esta logueado redireccion
    #if request.session.get('logueado', False):
     #       return redirect('/examen/')
    t = loader.get_template('login.html')
    if request.method == 'GET':
        #return render_to_response("formVerdaderoFalso.html")
        request_context = RequestContext(request, {})
        return HttpResponse(t.template.render(request_context))
    
    elif request.method == 'POST':
        
        user = request.POST.get('user', None)
        password = request.POST.get('password', None)

        # regresar error
        if not user.strip() or not password.strip():
            request_context = RequestContext(request,
                                             {'errores': ['Usuario o contraseña vacíos']})
            return HttpResponse(t.template.render(request_context))

        # comprobar credenciales
        try:
            alumno = models.Alumnos.objects.get(usuario=user, pass_field=password)
        except:
            request_context = RequestContext(request,
                                             {'errores': ['Usuario o contraseña inválidos']})
            return HttpResponse(t.template.render(request_context))

        if alumno.logueado: # solo se puede loguear una vez
            request_context = RequestContext(request,
                                             {'errores': ['Ya se inició sesión en otro lado']})
            return HttpResponse(t.template.render(request_context))
        
        # comprobar si ya habia una sesion anterior para los alumnos que cambien de compu
        if alumno.session_key and alumno.session_key != request.session.session_key:
            # recuperar datos de esa sesion en la nueva y borrar anterior por si las dudas
            antigua = Session.objects.get(pk=alumno.session_key)
            nueva = Session.objects.get(pk=request.session.session_key)
            nueva.session_data = antigua.session_data
            nueva.save()
            antigua.delete()
        
        if not alumno.session_key: # primer logueo generar examen
            ex = xml.examen.Examen(settings.XML)
            request.session['examen'] = ex

        request.session['nombre'] = alumno.nombre
        request.session['logueado'] = True
        alumno.session_key = request.session.session_key
        alumno.logueado = 1
        alumno.save()

        
        return redirect('/examen/')


def decidirContenido(nombreAlumno, examen, tipo='POST'):
    plantilla = 'finalizado.html'
    contexto = {'nombre': nombreAlumno}
    if tipo == 'POST':
        plantilla = 'contenidoExamen.html'
    else:
        plantilla = 'examen.html'
    if examen.orden: # todavia hay cosas aleatorias por contestar
        sec, inciso = examen.orden[0]
        etiquetaSec = examen.aleatorias[sec]
        contexto = {'nombre': nombreAlumno,
                    'instruccion': examen.getSeccion(sec).instruccion,
                'texto': examen.getInciso(sec, inciso).texto} # context
        if etiquetaSec == 'subrayar':
            contexto['opciones'] = examen.getInciso(sec, inciso).opciones
            contexto['template'] = 'formSubrayar.html'            
                
        elif etiquetaSec == 'verdaderoFalso':
            contexto['template'] = 'formVerdaderoFalso.html'
            
        elif etiquetaSec == 'abiertas':
            contexto['template'] = 'formAbiertas.html'            
    
    elif examen.alFinal: #misc y analisis
        etiquetaSec = examen.alFinal[0]
        objeto = examen.secciones['analisis']
        contexto['recursos'] = objeto.recursos
        contexto['incisos'] = objeto.incisos
        contexto['instruccion'] = objeto.instruccion
        if objeto.texto:
            contexto['texto']
        if etiquetaSec == 'analisis':
            contexto['template'] = 'formAnalisis.html'
        elif etiquetaSec == 'misc':
            contexto['template'] = 'formAnalisis.html'
    
        
    return plantilla, contexto

def procesarAleatoria():
    
    
@examenActivo
@logueado
def examen(request):

    examen = request.session.get('examen', None)
    if not examen:  # error fatal, no deberia ser posible
        redirect('/login/')

    plantilla = ''
    contexto = {}
    nombreAlumno = request.session.get('nombre', 'anonimo')
    if request.method == 'GET':
        plantilla, contexto = decidirContenido(nombreAlumno, examen, 'GET')

    elif request.method == 'POST':
        # consumir respuesta
        # esto solo sirve para aleatorias
        respuesta = request.POST.get('respuesta', None)
        if respuesta != None: # comprobar en BD
            respuesta = respuesta.strip()
            secI, inI = examen.orden[0]
            etiquetaSec = examen.aleatorias[secI]
            inciso = examen.getInciso(secI, inI)
            seccion = examen.getSeccion(secI)
            # obtener ejercicio de BD
            exeBD = models.Examenes.objects.get(pk=settings.ID_EXAMEN)
            ejercicio = models.Ejercicios.objects.get(idincisoxml=inciso.id, examenes_idexamen=exeBD)
            # obtener alumno de BD
            alumno = models.Alumnos.objects.get(session_key=request.session.session_key)
            alEj = models.AlumnosEjercicios()
            alEj.horasubida = datetime.datetime.now()
            alEj.puntosobtenidos = 0
            alEj.alumnos_idalumno = alumno
            alEj.ejercicios_idejercicios = ejercicio
            alEj.respuesta = respuesta
            print('Acaaaa: ', etiquetaSec)
            if etiquetaSec == 'subrayar':
                respuesta = int(respuesta)
                alEj.respuesta = xml.subrayar.descifrar(respuesta, examen.clave)
                alEj.calificado = 1
                if int(inciso.correcto) == respuesta: # bien Contestado
                    alEj.puntosobtenidos = seccion.puntajeUnitario

            elif etiquetaSec == 'verdaderoFalso':
                alEj.calificado = 1
                if inciso.correcto == respuesta:
                    alEj.puntosobtenidos = seccion.puntajeUnitario
                    
            alEj.save()

        # consumir siempre de post
        if examen.orden:
            del(examen.orden[0])
        else:
            if examen.alFinal:
                del(examen.alFinal[0])
        request.session['examen'] = examen # force sync
        plantilla, contexto = decidirContenido(nombreAlumno, examen, 'POST')
        
    request_context = RequestContext(request, contexto)
    t = loader.get_template(plantilla)
    return HttpResponse(t.template.render(request_context))

# vista con la funcionalidad de monitoreo
def monitoreo(request):
    if request.method == 'GET':
        host = settings.HOST_MONITOR
        port = settings.PUERTO_MONITOR
        caso = request.GET.get('caso', '')
        mySocket = socket.socket()
        mySocket.connect((host,port))
        nombre = request.session.get('nombre', 'anonimo')
        message = '%s %s de ventana' % (nombre, caso)
        mySocket.sendall(message.encode())
        mySocket.sendall('$$$'.encode())                 
        mySocket.close()
        
    return HttpResponse('')

