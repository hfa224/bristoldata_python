# settings.py

import os

MAPBOX_ACCESS_KEY = 'pk.eyJ1IjoiaGZhZGFtcyIsImEiOiJjazRlN2V4ajMwYTF0M2puOWxlNHE4MDVxIn0.msotFFt7QTzrehj8Gxs43g'

SECRET_KEY= os.environ.get('SECRET_KEY') or 'you-will-never-guess'