
import random
import django
from lxml import etree
import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "examenesEscritos.settings")
django.setup() # para utilizar elementos standalone

from modelo import models

especiales = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ñ': 'N'}

def filtrarEspeciales(letra):
    if letra in especiales:
        return especiales[letra]
    return letra

def pegar(palabra):
    res = ''
    for letra in palabra:
        res += filtrarEspeciales(letra)
    return res


def generar(archivo, id_grupo):
    for l in open(archivo):
        partes = l.split(' ')
        user = pegar(partes[0][0:2].upper()) + pegar(partes[1][0:2].upper()) + str(random.randint(0, 9)) + str(random.randint(0, 9))
        registrar(l, user, user, id_grupo)

def registrar(nombre, usuario, password, id_grupo):
    alumno = models.Alumnos(nombre=nombre, usuario=usuario, pass_field=password)
    alumno.logueado = 0
    alumno.session_key = ''
    alumno.save()
    
    grupo = models.Grupos.objects.get(pk=id_grupo)
    models.AlumnosGrupos(alumnos_idalumno=alumno, grupos_idgrupos=grupo).save()

if __name__ == '__main__':
    # path de archivo e id de grupo
    generar(sys.argv[1], sys.argv[2])
