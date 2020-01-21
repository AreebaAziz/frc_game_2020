import logging
import os 
import django 

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.DEBUG)



try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maceng.frc_game_2020.settings')
    os.environ["DISPLAY"]
except:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
django.setup()