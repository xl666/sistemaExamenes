
"""
Inicializa la BD con respecto a un examen creando los registros necesarios
También modifica el XML para agregar IDs apropiados (se recomienda mantener original)
"""

import django

from lxml import etree
import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "examenesEscritos.settings")
django.setup() # para utilizar elementos standalone

from modelo import models

def agregarIds(tree):
    idAux = 1
    for inciso in tree.xpath('//inciso'):
        inciso.set("id", str(idAux))
        idAux += 1

        
def crearExamenBD(tree, idGrupo):
    d = {}
    d['periodo'] = tree.xpath('/examen/periodo')[0].text
    d['tipo'] = tree.xpath('/examen/tipo')[0].text
    d['carrera'] = tree.xpath('/examen/carrera')[0].text
    d['universidad'] = tree.xpath('/examen/universidad')[0].text
    d['grupos_idgrupos'] = models.Grupos.objects.filter(pk=idGrupo)[0]
    ex = models.Examenes(**d)
    ex.save()
    return ex.pk

# para determinar el puntaje de un inciso si no es directo
def getPuntaje(elemento):
    #ir hacia arriba en los padres hasta encontrar
    while elemento is not None:
        res = elemento.get('puntaje')
        if res:
            return res
        elemento = elemento.getparent()

        
def crearRegistrosEjercicios(tree, idExamen):
    for inciso in tree.xpath('//inciso'):
        d = {}
        d['idincisoxml'] = inciso.get('id')
        correcto = inciso.get('correcto')
        if not correcto:
            correcto = ''
        d['correcto'] = correcto
        d['puntaje'] = getPuntaje(inciso)
        d['examenes_idexamen'] = models.Examenes.objects.filter(pk=idExamen)[0]
        ej = models.Ejercicios(**d)
        ej.save()

    
def inicializar(xml, salidaXML, idGrupo):
    """
     Se regresa el id del examen creado para que sea más facil la configuración
    """
    tree = etree.parse(xml)
    # agregar ids apropiados a cada inciso
    agregarIds(tree)
    # crear registro en examenes
    idExamen = crearExamenBD(tree, idGrupo)
    # crear registros de ejercicios
    crearRegistrosEjercicios(tree, idExamen)

    #guardar nuevo xml con ids adecuados
    with open(salidaXML, 'w') as ar:
        ar.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        ar.write(etree.tostring(tree, pretty_print=True, encoding='unicode'))

    # resetear alumnos
    models.Alumnos.objects.all().update(logueado=0, session_key='')
    
    return idExamen

if __name__ == '__main__':
    #el ultimo argumento es el id del grupo
    print(inicializar(sys.argv[1], sys.argv[2], int(sys.argv[3])))
