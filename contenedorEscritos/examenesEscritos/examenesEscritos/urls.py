"""examenesEscritos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin
from examenesEscritos.views import *
from examenesEscritos import settings

urlpatterns = [
    path('%sadmin/' % settings.PATH_PREFIX, admin.site.urls, name='admin'),
    path('%slogin/' % settings.PATH_PREFIX, login, name='login'),
    path('%sexamen/' % settings.PATH_PREFIX, examen, name='examen'),
    path('%s' % settings.PATH_PREFIX, examen, name='index'),
    path('%smonitoreo/' % settings.PATH_PREFIX, monitoreo, name='monitoreo'),
    path('%salmacenarPendiente/' % settings.PATH_PREFIX, almacenarPendiente, name='almacenarPendiente'),
    path('%sregresarPendiente/' % settings.PATH_PREFIX, regresarPendiente, name='regresarPendiente'),
]
