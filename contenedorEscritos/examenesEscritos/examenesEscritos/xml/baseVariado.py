"""
Clase base para Misc y Analisis que son casi iguales
"""


from lxml import etree
from random import shuffle



class Recurso():
    """Opcion de subrayar

    """
    def __init__(self, recurso):
        self.tipo = recurso.tag
        self.src = recurso.get('src')
        

class Inciso():
    """Inciso de subrayar

    """
    def __init__(self, inciso):
        self.texto = inciso.xpath('./texto')[0].text
        self.puntaje = int(inciso.get('puntaje'))
        self.id = inciso.get('id')
        

class BaseVariado():
    """Representa una seccion de subrayar, sólo debe haber una en el examen
    """
    def __init__(self, elemento, xml):
        tree = etree.parse(xml)
        todo = tree.xpath('//*[@tipo="%s"]' % elemento)
        if len(todo) != 1:
            self.incisos = []
            return
        todo = todo[0]
        self.puntajeTotal = sum([int(ii.get('puntaje')) for ii in  todo.xpath('.//inciso')])
        self.incisos = [Inciso(ins) for ins in todo.xpath('.//inciso')]
        self.instruccion = todo.xpath('.//instruccion')[0].text.strip()
        self.texto = todo.xpath('.//texto')[0].text
        self.recursos = [Recurso(rec) for rec in todo.xpath('.//recursos/child::*')]




