

from examenesEscritos.xml.baseVariado import BaseVariado

                       
        
class Analisis(BaseVariado):
    """Representa una seccion de subrayar, sólo debe haber una en el examen
    """
    def __init__(self, xml):
        BaseVariado.__init__(self, 'analisis', xml)





