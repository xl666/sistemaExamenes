from django.contrib import admin

# Register your models here.

from modelo.models import *


class IncisosFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Inciso'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'inciso'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        qs = model_admin.get_queryset(request)
        grupo = request.GET.get('ejercicios_idejercicios__examenes_idexamen__grupos_idgrupos__idgrupos__exact', None)
        tipo = request.GET.get('ejercicios_idejercicios__examenes_idexamen__tipo', None)
        if grupo and tipo:
            try:
                grupoModelo = Grupos.objects.get(pk=grupo)
                examenModelo = Examenes.objects.get(grupos_idgrupos=grupoModelo,
                                               tipo__icontains=tipo)

            except:
                print('EROROROROROROROROR')
                return ()
            incisos = Ejercicios.objects.filter(examenes_idexamen=examenModelo)
            elementos = [('%s:%s' % (examenModelo.pk, inc.idincisoxml) ,inc.idincisoxml) for inc in incisos]
            return tuple(elementos)
            
        return ()

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if not self.value():
            return queryset
        
        idExamen, idxml = tuple(self.value().split(':'))
        examenModelo = Examenes.objects.get(pk=idExamen)
        ejercicioModelo = Ejercicios.objects.filter(examenes_idexamen=examenModelo,
                                                    idincisoxml=idxml)
        return queryset.filter(ejercicios_idejercicios=ejercicioModelo[0])


class AlumnosFilter(admin.SimpleListFilter):
    title = 'Alumno'
    parameter_name = 'nombre'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        grupo = request.GET.get('ejercicios_idejercicios__examenes_idexamen__grupos_idgrupos__idgrupos__exact', None)
        if grupo:
            try:
                grupoModelo = Grupos.objects.get(pk=grupo)
                alumnosGruposModelo = AlumnosGrupos.objects.filter(grupos_idgrupos=grupoModelo)                 
            except:
                return ()
            alumnos = [alu.alumnos_idalumno for alu in alumnosGruposModelo]
            elementos = [(alu.pk , alu.nombre) for alu in alumnos]
            return tuple(elementos)
            
        return ()

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if not self.value():
            return queryset
        alumnoModel = Alumnos.objects.get(pk=self.value())
        return queryset.filter(alumnos_idalumno=alumnoModel)        


def concatenarAlumnos(alumnosModelo):
    res = Alumnos.objects.filter(pk=alumnosModelo[0].alumnos_idalumno.pk)
    for i in range(1, len(alumnosModelo)):
        res = res | Alumnos.objects.filter(pk=alumnosModelo[i].alumnos_idalumno.pk)
    return res

class GrupoFilter(admin.SimpleListFilter):
    title = 'Grupo'
    parameter_name = 'grupo'
    def lookups(self, request, model_admin):
        gruposModelo = Grupos.objects.all()
        return tuple([(gr.pk, gr.__str__()) for gr in gruposModelo])

    def queryset(self, request, queryset):
        alumnosModelo = AlumnosGrupos.objects.filter(grupos_idgrupos=self.value())
        if len(alumnosModelo) == 0:
            return queryset
        return concatenarAlumnos(alumnosModelo)

class AlumnosAdmin(admin.ModelAdmin):
    list_filter = (GrupoFilter, 'nombre')
    
class AlumnosEjerciciosAdmin(admin.ModelAdmin):
    list_filter = ('ejercicios_idejercicios__examenes_idexamen__grupos_idgrupos', 'ejercicios_idejercicios__examenes_idexamen__tipo', IncisosFilter, 'calificado', AlumnosFilter)
    
admin.site.register(Alumnos, AlumnosAdmin)
admin.site.register(AlumnosEjercicios, AlumnosEjerciciosAdmin)
admin.site.register(AlumnosGrupos)
admin.site.register(Ejercicios)
admin.site.register(Examenes)
admin.site.register(Grupos)
