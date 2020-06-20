
"""
Modulo con diversos decoradores utilies
"""

from examenesEscritos import settings
from django.shortcuts import render
from django.shortcuts import redirect

def examenActivo(fun):
    def interna(*args, **kargs):
        
        if settings.ACTIVO:
            return fun(*args, **kargs)

        return render('desactivado.html')

    return interna

def logueado(fun):
    def interna(request, *args, **kargs):        
        if not request.session.get('logueado', False):
            return redirect('/login/')
        return fun(request, *args, **kargs)

    return interna
