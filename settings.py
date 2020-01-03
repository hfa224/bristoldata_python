# settings.py

import os

MAPBOX_ACCESS_KEY = os.environ.get('MAPBOX_ACCESS_KEY') or 'you-will-never-guess'

SECRET_KEY= os.environ.get('SECRET_KEY') or 'you-will-never-guess'