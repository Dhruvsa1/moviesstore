"""Copy to /var/www/ddhruvsa1_pythonanywhere_com_wsgi.py on PythonAnywhere."""
import os
import sys

path = '/home/ddhruvsa1/moviesstore'
if path not in sys.path:
    sys.path.insert(0, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'moviesstore.settings'
os.environ['DJANGO_DEBUG'] = 'false'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
