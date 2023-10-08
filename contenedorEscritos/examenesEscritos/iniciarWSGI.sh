#!/bin/bash


#uwsgi --http :8000 --module examenesEscritos.wsgi --env DJANGO_SETTINGS_MODULE=examenesEscritos.settings

uwsgi --socket :8001 --module examenesEscritos.wsgi --env DJANGO_SETTINGS_MODULE=examenesEscritos.settings --processes 8
