
from django.shortcuts import render
from examenesEscritos.decoradores import *
from modelo import models
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.shortcuts import redirect
import examenesEscritos.xml.examen 
import examenesEscritos.xml.subrayar
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
            ex = examenesEscritos.xml.examen.Examen(settings.XML)
            request.session['examen'] = ex
            request.session['pendientes'] = []

        request.session['nombre'] = alumno.nombre
        request.session['logueado'] = True
        alumno.session_key = request.session.session_key
        alumno.logueado = 1
        alumno.save()
        return redirect('/examen/')


def calcularRestantes(examen, pendientes):
    return len(examen.orden) + len(examen.alFinal) + len(pendientes)


def decidirContenido(nombreAlumno, request, tipo='POST'):
    examen = request.session.get('examen', None)
    pendientes = request.session.get('pendientes', [])
    pendientes = request.session.get('pendientes', [])
    plantilla = 'finalizado.html'
    contexto = {'nombre': nombreAlumno, 'restantes': calcularRestantes(examen, pendientes)}
    #ya no mostrar boton de agregar a pendientes si ya no se puede
    ban = (calcularRestantes(examen, pendientes) - len(examen.alFinal)) > 1
    contexto['agregar'] = ban
    if pendientes and not examen.orden: #cuando solo quedan pendientes
        elemento = pendientes[0]
        del(pendientes[0])
        examen.orden.insert(0, elemento)
        request.session['examen'] = examen # force sync
        request.session['pendientes'] = pendientes

    if examen.orden:  # todavia hay cosas aleatorias por contestar
        if tipo == 'POST':
            plantilla = 'contenidoExamen.html'
        else:
            plantilla = 'examen.html'
        sec, inciso = examen.orden[0]
        etiquetaSec = examen.aleatorias[sec]
        contexto['instruccion'] = examen.getSeccion(sec).instruccion
        contexto['puntos'] = examen.getSeccion(sec).puntajeUnitario
        contexto['texto'] = examen.getInciso(sec, inciso).texto
        if etiquetaSec == 'subrayar':
            contexto['opciones'] = examen.getInciso(sec, inciso).opciones
            contexto['template'] = 'formSubrayar.html'
                
        elif etiquetaSec == 'verdaderoFalso':
            contexto['template'] = 'formVerdaderoFalso.html'
            
        elif etiquetaSec == 'abiertas':
            contexto['template'] = 'formAbiertas.html'
    elif examen.alFinal:  # relacionar, misc y analisis
        if tipo == 'POST':
            plantilla = 'contenidoExamen.html'
        else:
            plantilla = 'examen.html'
        etiquetaSec = examen.alFinal[0]
        objeto = examen.secciones[etiquetaSec]
        contexto['recursos'] = objeto.recursos
        contexto['incisos'] = objeto.incisos
        contexto['instruccion'] = objeto.instruccion
        if objeto.texto:
            contexto['texto'] = objeto.texto
        if etiquetaSec == 'analisis':
            contexto['template'] = 'formAnalisis.html'
        elif etiquetaSec == 'misc':
            contexto['template'] = 'formAnalisis.html'
        elif etiquetaSec == 'relacionar':
            contexto['opciones'] = objeto.opciones
            contexto['template'] = 'formRelacionar.html'
    
    return plantilla, contexto


# solo analisis y misc
def procesarNoAleatoria(examen, request, relacionar=False):
    respuestas = [k for k in request.POST.keys() if k.startswith('respuesta')]
    ids = [ele.split('respuesta')[1] for ele in respuestas]
    exeBD = models.Examenes.objects.get(pk=settings.ID_EXAMEN)
    alumno = models.Alumnos.objects.get(session_key=request.session.session_key)
    for i in range(len(respuestas)):
        alEj = models.AlumnosEjercicios()
        alEj.horasubida = datetime.datetime.now()
        alEj.puntosobtenidos = 0
        alEj.alumnos_idalumno = alumno
        ejercicio = models.Ejercicios.objects.get(idincisoxml=ids[i], examenes_idexamen=exeBD)
        alEj.ejercicios_idejercicios = ejercicio
        if len(models.AlumnosEjercicios.objects.filter(alumnos_idalumno=alumno, ejercicios_idejercicios=ejercicio)) > 0:
            return #no se debe volver a procesar
        alEj.respuesta = request.POST.get(respuestas[i], '')
        #para relacionar
        if relacionar:
            alEj.calificado = 1
            if alEj.respuesta.strip().lower() == ejercicio.correcto:                
                alEj.puntosobtenidos = examen.secciones['relacionar'].puntajeUnitario
        alEj.save()

def procesarRelacionar(examen, request):
    procesarNoAleatoria(examen, request, True)
        
def procesarAleatoria(respuesta, examen, request):
    secI, inI = examen.orden[0]
    etiquetaSec = examen.aleatorias[secI]
    inciso = examen.getInciso(secI, inI)
    seccion = examen.getSeccion(secI)
    # obtener ejercicio de BD
    exeBD = models.Examenes.objects.get(pk=settings.ID_EXAMEN)
    ejercicio = models.Ejercicios.objects.get(idincisoxml=inciso.id, examenes_idexamen=exeBD)
    # obtener alumno de BD
    alumno = models.Alumnos.objects.get(session_key=request.session.session_key)
    #comprobar si el registro ya se habia hecho
    if len(models.AlumnosEjercicios.objects.filter(alumnos_idalumno=alumno, ejercicios_idejercicios=ejercicio)) > 0:
        return #no se debe volver a procesar
    
    alEj = models.AlumnosEjercicios()
    alEj.horasubida = datetime.datetime.now()
    alEj.puntosobtenidos = 0
    alEj.alumnos_idalumno = alumno
    alEj.ejercicios_idejercicios = ejercicio
    alEj.respuesta = respuesta
    if etiquetaSec == 'subrayar':
        respuesta = int(respuesta)
        alEj.respuesta = examenesEscritos.xml.subrayar.descifrar(respuesta, examen.clave)
        alEj.calificado = 1
        if int(inciso.correcto) == respuesta: # bien Contestado
            alEj.puntosobtenidos = seccion.puntajeUnitario


    elif etiquetaSec == 'verdaderoFalso':
        alEj.calificado = 1
        if inciso.correcto == respuesta:
            alEj.puntosobtenidos = seccion.puntajeUnitario
                
    alEj.save()
    
@examenActivo
@logueado
def examen(request):

    examen = request.session.get('examen', None)
    if not examen:  # error fatal, no deberia ser posible
        redirect('/login/')
    contexto = {}
    plantilla = ''
    nombreAlumno = request.session.get('nombre', 'anonimo')
    if request.method == 'GET':
        plantilla, contexto = decidirContenido(nombreAlumno, request, 'GET')
        contexto['universidad'] = examen.universidad
        contexto['carrera'] = examen.carrera
        contexto['tipoExamen'] = examen.tipo
        contexto['periodo'] = examen.periodo
        err = request.session.get('error', '')
        contexto['error'] = err
        nums = [i for i in range(len(request.session.get('pendientes', [])))]
        contexto['pendientes'] = nums
        request.session['error'] = ''
        
        
    elif request.method == 'POST':
        # consumir respuesta
        if examen.orden:
            respuesta = request.POST.get('respuesta', None)
            if respuesta != None: # comprobar en BD
                respuesta = respuesta.strip()
                procesarAleatoria(respuesta, examen, request)

        elif examen.alFinal:
            if examen.alFinal[0] == 'relacionar':
                procesarRelacionar(examen, request)
            else:
                procesarNoAleatoria(examen, request)
                
        # consumir siempre de post
        if examen.orden:
            del(examen.orden[0])
        else:
            if examen.alFinal:
                del(examen.alFinal[0])
        request.session['examen'] = examen # force sync
        plantilla, contexto = decidirContenido(nombreAlumno, request, 'POST')
        nums = [i for i in range(len(request.session.get('pendientes', [])))]
        contexto['pendientes'] = nums
        err = request.session.get('error', '')
        contexto['error'] = err
        request.session['error'] = ''

    
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

#para almacenar un ejercicio pendiente si hay espacio
def almacenarPendiente(request):
    examen = request.session.get('examen', None)
    
    if request.method == 'GET':
        if not examen.orden:
            request.session['error'] = 'Ya no es posible agregar más ejercicios pendientes'
            return redirect('/examen/') #mientras haya aleatorias se puede hacer
        pendientes = request.session.get('pendientes', [])
        if len(pendientes) >= settings.MAX_PENDIENTES: #ya no se puede
            request.session['error'] = 'Ya no puedes agregar más ejercicios pendientes, el máximo es %s' % settings.MAX_PENDIENTES
            return redirect('/examen/')
        pendientes.append(examen.orden[0])
        del(examen.orden[0])
        request.session['examen'] = examen # force sync
        request.session['pendientes'] = pendientes
        return redirect('/examen/')
        
def regresarPendiente(request):
    if request.method == 'POST':
        return redirect('/examen/')
    indice = request.GET.get('indice', -1)
    examen = request.session.get('examen', None)
    pendientes = request.session.get('pendientes', [])
    if pendientes and int(indice) > -1 and int(indice) < len(pendientes):
        elemento = pendientes[int(indice)]
        del(pendientes[int(indice)])
        examen.orden.insert(0, elemento)
        request.session['examen'] = examen # force sync
        request.session['pendientes'] = pendientes

    return redirect('/examen/')
