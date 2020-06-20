
from lxml import etree
from random import shuffle


class Opcion():
    """Opcion de subrayar

    """
    def __init__(self, opcion):
        self.id = opcion.get('id')
        self.texto = opcion.text.strip()
        

class Inciso():
    """Inciso de subrayar

    """
    def __init__(self, inciso):
        self.texto = inciso.xpath('./texto')[0].text.strip()
        self.correcto = inciso.get('correcto')
        self.id = inciso.get('id')        

class Relacionar():
    """Representa una seccion de relacionar, sólo debe haber una en el examen
    """
    def __init__(self, xml):
        tree = etree.parse(xml)
        todo = tree.xpath('//*[@tipo="relacionar"]')
        if len(todo) != 1:
            self.incisos = []
            self.opciones = []
            return
        todo = todo[0]
        self.recursos = []
        self.puntajeUnitario = int(todo.get('puntaje'))
        self.puntajeTotal = len(todo.xpath('.//inciso')) * self.puntajeUnitario
        self.incisos = [Inciso(ins) for ins in todo.xpath('.//inciso')]
        self.opciones = [Opcion(op) for op in todo.xpath('.//opcion')]
        shuffle(self.incisos)
        self.texto = ''
        self.instruccion = todo.xpath('.//instruccion')[0].text.strip()





