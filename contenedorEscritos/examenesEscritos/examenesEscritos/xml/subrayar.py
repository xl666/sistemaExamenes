
from lxml import etree
from random import shuffle

def cifrar(original, clave):
    return str(ord(original) * clave)

def descifrar(cifrado, clave):
    return chr(cifrado//clave)

class Opcion():
    """Opcion de subrayar

    """
    def __init__(self, opcion, clave):
        self.id = cifrar(opcion.get('id'), clave)
        self.texto = opcion.text.strip()
        

class Inciso():
    """Inciso de subrayar

    """
    def __init__(self, inciso, clave):
        self.opciones = [Opcion(op, clave) for op in inciso.xpath('.//opcion')]
        self.texto = inciso.xpath('./texto')[0].text.strip()
        self.correcto = cifrar(inciso.get('correcto'), clave)
        self.id = inciso.get('id')
        shuffle(self.opciones)
        

class Subrayar():
    """Representa una seccion de subrayar, sólo debe haber una en el examen
    """
    def __init__(self, xml, clave):
        tree = etree.parse(xml)
        todo = tree.xpath('//*[@tipo="subrayar"]')
        if len(todo) != 1:
            self.incisos = []
            return
        todo = todo[0]
        self.puntajeUnitario = int(todo.get('puntaje'))
        self.puntajeTotal = len(todo.xpath('.//inciso')) * self.puntajeUnitario
        self.incisos = [Inciso(ins, clave) for ins in todo.xpath('.//inciso')]
        shuffle(self.incisos)
        self.instruccion = todo.xpath('.//instruccion')[0].text.strip()





