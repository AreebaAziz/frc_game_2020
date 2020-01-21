"""
WSGI config for frc_game_2020 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import time
import traceback
import signal
import sys
from django.core.wsgi import get_wsgi_application

try:
    application = get_wsgi_application()
    print 'WSGI without exception'
except Exception:
    print 'handling WSGI exception'
    # Error loading applications
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)

from django.core.wsgi import get_wsgi_application

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maceng.frc_game_2020.settings')
except:
    os.environ["SDL_VIDEODRIVER"] = "dummy"

application = get_wsgi_application()
