# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Alumnos(models.Model):
    idalumno = models.AutoField(db_column='idAlumno', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=150)
    usuario = models.CharField(max_length=8, blank=True, null=True)
    pass_field = models.CharField(db_column='pass', max_length=8, blank=True, null=True)  # Field renamed because it was a Python reserved word.
    logueado = models.IntegerField(blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Alumnos'

    def __str__(self):
        return '%s %s' % (self.idalumno, self.nombre)


class AlumnosEjercicios(models.Model):
    idalumnos_ejercicios = models.AutoField(db_column='idAlumnos_Ejercicios', primary_key=True)  # Field name made lowercase.
    respuesta = models.TextField()
    horasubida = models.DateTimeField(db_column='horaSubida')  # Field name made lowercase.
    calificado = models.IntegerField(blank=True, null=True)
    alumnos_idalumno = models.ForeignKey(Alumnos, models.DO_NOTHING, db_column='Alumnos_idAlumno')  # Field name made lowercase.
    ejercicios_idejercicios = models.ForeignKey('Ejercicios', models.DO_NOTHING, db_column='Ejercicios_idEjercicios')  # Field name made lowercase.
    puntosobtenidos = models.DecimalField(db_column='puntosObtenidos', max_digits=10, decimal_places=0, verbose_name='puntos')  # Field name made lowercase.

    def __str__(self):
        if self.calificado:
            return "Calificado: %s %s" % (self.alumnos_idalumno, self.ejercicios_idejercicios)
        return '%s:%s' % (self.alumnos_idalumno, self.ejercicios_idejercicios)
        
    class Meta:
        managed = False
        db_table = 'Alumnos_Ejercicios'


class AlumnosGrupos(models.Model):
    idalumnos_grupos = models.AutoField(db_column='idAlumnos_Grupos', primary_key=True)  # Field name made lowercase.
    alumnos_idalumno = models.ForeignKey(Alumnos, models.DO_NOTHING, db_column='Alumnos_idAlumno')  # Field name made lowercase.
    grupos_idgrupos = models.ForeignKey('Grupos', models.DO_NOTHING, db_column='Grupos_idGrupos')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Alumnos_Grupos'

    def __str__(self):
        return '%s %s' % (self.alumnos_idalumno, self.grupos_idgrupos)

class Ejercicios(models.Model):
    idejercicios = models.AutoField(db_column='idEjercicios', primary_key=True)  # Field name made lowercase.
    idincisoxml = models.CharField(db_column='idIncisoXML', max_length=45)  # Field name made lowercase.
    correcto = models.CharField(max_length=45, blank=True, null=True)
    puntaje = models.DecimalField(max_digits=10, decimal_places=0)
    examenes_idexamen = models.ForeignKey('Examenes', models.DO_NOTHING, db_column='Examenes_idExamen')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Ejercicios'

    def __str__(self):
        return '%s, ejercicio:%s' % (self.examenes_idexamen.__str__(), self.idincisoxml)


class Examenes(models.Model):
    idexamen = models.AutoField(db_column='idExamen', primary_key=True)  # Field name made lowercase.
    tipo = models.CharField(max_length=45, blank=True, null=True)
    periodo = models.CharField(max_length=45, blank=True, null=True)
    carrera = models.CharField(max_length=45, blank=True, null=True)
    universidad = models.CharField(max_length=45, blank=True, null=True)
    grupos_idgrupos = models.ForeignKey('Grupos', models.DO_NOTHING, db_column='Grupos_idGrupos')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Examenes'

    def __str__(self):
        return '%s. %s %s %s' % (self.idexamen, self.carrera, self.periodo, self.tipo)



class Grupos(models.Model):
    idgrupos = models.AutoField(db_column='idGrupos', primary_key=True)  # Field name made lowercase.
    periodo = models.CharField(max_length=45, blank=True, null=True)

    nombre = models.CharField(max_length=45, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'Grupos'

    def __str__(self):
        return '%s. %s %s' % (self.idgrupos, self.nombre, self.periodo)
