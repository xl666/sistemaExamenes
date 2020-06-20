
from lxml import etree
from random import shuffle



        

class Inciso():
    """Inciso de verdadero falso

    """
    def __init__(self, inciso):        
        self.texto = inciso.xpath('./texto')[0].text.strip()
        self.id = inciso.get('id')
        

class Abiertas():
    """Representa una seccion de preguntas abiertas, sólo debe haber una en el examen
    """
    def __init__(self, xml):
        tree = etree.parse(xml)
        todo = tree.xpath('//*[@tipo="abiertas"]')
        if len(todo) != 1:
            self.incisos = []
            return
        todo = todo[0]
        self.puntajeUnitario = int(todo.get('puntaje'))
        self.puntajeTotal = len(todo.xpath('.//inciso')) * self.puntajeUnitario
        self.incisos = [Inciso(ins) for ins in todo.xpath('.//inciso')]
        shuffle(self.incisos)
        self.instruccion = todo.xpath('.//instruccion')[0].text.strip()





