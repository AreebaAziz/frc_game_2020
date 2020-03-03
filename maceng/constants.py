from os.path import abspath, dirname

# Paths
BASE_PATH = abspath(dirname(dirname(__file__)))
FONT_PATH = BASE_PATH + '/fonts/'
IMAGE_PATH = BASE_PATH + '/images/'
SOUND_PATH = BASE_PATH + '/sounds/'

# Colors (R, G, B)
WHITE = (255, 255, 255)
GRAY = (102, 102, 102)
GREEN = (78, 255, 87)
YELLOW = (241, 255, 0)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)
FIREBALL = (248,180,5)
# Other
FONT = FONT_PATH + 'space_invaders.ttf'