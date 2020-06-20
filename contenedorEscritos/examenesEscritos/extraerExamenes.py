


import django

from lxml import etree
import sys
import os
import shutil

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "examenesEscritos.settings")
django.setup() # para utilizar elementos standalone

from modelo import models


def tipoInciso(inciso):
    aux = inciso.getparent()
    while aux != None:
        tipo = aux.get('tipo', None)
        if tipo:
            return tipo
        aux = aux.getparent()
    return None
    


def regresarRespuestaAlumno(inciso, alumno, examen, conPuntaje=False):
    """
    Regresa el texto de una pregunta y la respueta del alumno
    """
    res = 'Pregunta:\n'
    idXML = inciso.get('id')
    
    res += inciso.xpath('texto')[0].text.strip() + '\n'

    ejercicio = models.Ejercicios.objects.get(
        examenes_idexamen=examen, idincisoxml=idXML)
    alumnEj = models.AlumnosEjercicios.objects.get(
        ejercicios_idejercicios=ejercicio,
        alumnos_idalumno=alumno)

    res += '\nRespuesta del alumno: \n'
    res += alumnEj.respuesta

    if conPuntaje:
        res += '\nPuntos obtenidos por el alumno: %s' % alumnEj.puntosobtenidos

    res += '\n****************************************\n'

    return res,alumnEj.puntosobtenidos
        

def evaluacionAlumno(idAlumno, idExamen, examenXML, tipos=['subrayar', 'relacionar', 'verdadero_falso', 'abiertas', 'misc', 'analisis']):
    tree = etree.parse(examenXML)
    alumno = models.Alumnos.objects.get(pk=idAlumno)
    examen = models.Examenes.objects.get(pk=idExamen)
    contenido = alumno.nombre + '\n\n'
    sumaPuntos = 0
    for inciso in tree.xpath('//inciso'):
        if tipoInciso(inciso) in tipos:
            respuesta, puntos = regresarRespuestaAlumno(inciso, alumno, examen, True)
            contenido += respuesta
            sumaPuntos += puntos
    contenido += '\nPuntos totales: %s' % sumaPuntos
    return contenido

def crearArchivoRespuestas(directorioSalida, nombre, contenido):
    ruta = '%s/%s' % (directorioSalida, nombre)
    os.mkdir(ruta)
    with open('%s/%s' % (ruta, 'escrito.txt'), 'w') as archivo:
        archivo.write(contenido)
            
def extraerEvaluacionCurso(pathArchivoRelacion, pathSalida):
    """
    pathArchivoRelacion sigue el formato:
    nombreExamen,idExamen,idMejorAlumno,idMedioAlumno,idPeorAlumno,pathExamenIds.xml
    """
    with open(pathArchivoRelacion) as archivo:
        for linea in archivo:
            directorio, idExamen, idMejor, idEnmedio, idPeor, rutaExamen = linea.split(',')
            rutaExamen = rutaExamen.strip()
            salida = '%s/%s' % (pathSalida, directorio)
            os.mkdir(salida)
            shutil.copy(rutaExamen, '%s/examenEscrito.xml' % salida)
            contenido = evaluacionAlumno(idMejor, idExamen, rutaExamen)
            crearArchivoRespuestas(salida, 'mejor', contenido)
            contenido = evaluacionAlumno(idEnmedio, idExamen, rutaExamen)
            crearArchivoRespuestas(salida, 'medio', contenido)
            contenido = evaluacionAlumno(idPeor, idExamen, rutaExamen)
            crearArchivoRespuestas(salida, 'peor', contenido)

if __name__ == '__main__':
    pathArchivoRelacion = sys.argv[1]
    pathSalida = sys.argv[2]
    extraerEvaluacionCurso(pathArchivoRelacion, pathSalida)
