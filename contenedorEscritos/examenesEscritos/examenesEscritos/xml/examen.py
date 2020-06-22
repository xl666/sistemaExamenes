"""
Modulo para integrar un examen
"""

from lxml import etree
from examenesEscritos.xml.subrayar import Subrayar
from examenesEscritos.xml.verdaderoFalso import VerdaderoFalso
from examenesEscritos.xml.abiertas import Abiertas
from examenesEscritos.xml.misc import Misc
from examenesEscritos.xml.analisis import Analisis
from examenesEscritos.xml.relacionar import Relacionar
import random

class Examen():
    """Representa a un examen, llevando su control
    
    """
    def __init__(self, xml):
        tree = etree.parse(xml)
        self.secciones = {}
        self.universidad = tree.xpath('./universidad')[0].text
        self.carrera = tree.xpath('./carrera')[0].text
        self.tipo = tree.xpath('./tipo')[0].text
        self.periodo = tree.xpath('./periodo')[0].text
        self.secciones['subrayar'] = None
        self.secciones['verdaderoFalso'] = None
        self.secciones['abiertas'] = None
        self.secciones['misc'] = None
        self.secciones['analisis'] = None
        self.secciones['relacionar'] = None
        self.clave = random.randint(10000000, 999999999)
        if tree.xpath('//*[@tipo="subrayar"]'):
            self.secciones['subrayar'] = Subrayar(xml, self.clave)

        if tree.xpath('//*[@tipo="verdadero_falso"]'):
            self.secciones['verdaderoFalso'] = VerdaderoFalso(xml)

        if tree.xpath('//*[@tipo="abiertas"]'):
            self.secciones['abiertas'] = Abiertas(xml)

        if tree.xpath('//*[@tipo="misc"]'):
            self.secciones['misc'] = Misc(xml)

        if tree.xpath('//*[@tipo="analisis"]'):
            self.secciones['analisis'] = Analisis(xml)

        if tree.xpath('//*[@tipo="relacionar"]'):
            self.secciones['relacionar'] = Relacionar(xml)

        self.aleatorias = [] #se van a revolver
        if self.secciones['subrayar'] != None:
            self.aleatorias.append('subrayar')
        if self.secciones['verdaderoFalso'] != None:
            self.aleatorias.append('verdaderoFalso')
        if self.secciones['abiertas'] != None:
            self.aleatorias.append('abiertas')
        
        self.alFinal = [] #aparecen al final
        if self.secciones['relacionar'] != None:
            self.alFinal.append('relacionar')
        if self.secciones['analisis'] != None:
            self.alFinal.append('analisis')
        if self.secciones['misc'] != None:
            self.alFinal.append('misc')

        self._generarOrden()

    def _generarOrden(self):
        self.orden = []
        i = 0
        for sec in self.aleatorias:
            self.orden += [(i, elem) for elem in range(len(self.secciones[sec].incisos))]
            i += 1
        random.shuffle(self.orden)

    #regresa una seccion de acuerdo al indice de orden
    def getSeccion(self, sec):
        return self.secciones[self.aleatorias[sec]]
        
    def getInciso(self, sec, inc):        
        return self.getSeccion(sec).incisos[inc]
        
    
