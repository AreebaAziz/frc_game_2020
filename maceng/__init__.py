import logging
import os 
import django 

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.DEBUG)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maceng.frc_game_2020.settings')
django.setup()
