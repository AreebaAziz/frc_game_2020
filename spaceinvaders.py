#!/usr/bin/env python

# Space Invaders
# Created by Lee Robinson

import logging
from pygame import *
import sys
from os.path import abspath, dirname
from os import environ
from random import choice

### ****************************************************** ####
### ********************* constants.py ******************* ####
### ****************************************************** ####

# Paths
BASE_PATH = abspath(dirname(__file__))
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

# Other
FONT = FONT_PATH + 'space_invaders.ttf'

SCREEN = display.set_mode((800, 600))
# SCREEN = display.set_mode((0, 0), FULLSCREEN)
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = 800, 600

IMG_NAMES = ['ship', 'mystery',
             'enemy1_1', 'enemy1_2',
             'enemy2_1', 'enemy2_2',
             'enemy3_1', 'enemy3_2',
             'explosionblue', 'explosiongreen', 'explosionpurple',
             'laser', 'enemylaser']
IMAGES = {name: image.load(IMAGE_PATH + '{}.png'.format(name)).convert_alpha()
          for name in IMG_NAMES}

BLOCKERS_POSITION = 450
ENEMY_DEFAULT_POSITION = 65  # Initial value for a new game
ENEMY_MOVE_DOWN = 35

### ****************************************************** ####
### ********************* spaceinvaders.py *************** ####
### ****************************************************** ####

def _scale_img(img):
    ix, iy = img.get_size()
    nx, ny = int(ix * get_width_inc()), int(iy * get_height_inc())
    return transform.scale(img, (nx, ny))

class Ship(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = _scale_img(IMAGES['ship'])
        self.rect = self.image.get_rect(topleft=(int(375 * get_width_inc()), int(540 * get_height_inc())))
        self.speed = int(5 * get_width_inc())

    def update(self, keys, *args):
        if keys[K_LEFT] and self.rect.x > int(10 * get_width_inc()):
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < int(740 * get_width_inc()):
            self.rect.x += self.speed
        game.screen.blit(self.image, self.rect)


class Bullet(sprite.Sprite):
    def __init__(self, xpos, ypos, direction, speed, filename, side):
        sprite.Sprite.__init__(self)
        self.image = _scale_img(IMAGES[filename])
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        self.speed = speed
        self.direction = direction
        self.side = side
        self.filename = filename

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)
        self.rect.y += self.speed * self.direction
        if self.rect.y < int(15 * get_height_inc()) or self.rect.y > int(600 * get_height_inc()):
            self.kill()


class Enemy(sprite.Sprite):
    def __init__(self, row, column):
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.images = []
        self.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()

    def toggle_image(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def update(self, *args):
        game.screen.blit(self.image, self.rect)

    def load_images(self):
        images = {0: ['1_2', '1_1'],
                  1: ['2_2', '2_1'],
                  2: ['2_2', '2_1'],
                  3: ['3_1', '3_2'],
                  4: ['3_1', '3_2'],
                  }
        img1, img2 = (IMAGES['enemy{}'.format(img_num)] for img_num in
                      images[self.row])

        img1, img2 = transform.scale(img1, (40, 35)), transform.scale(img2, (40, 35))
        self.images.append(_scale_img(img1))
        self.images.append(_scale_img(img2))


class EnemiesGroup(sprite.Group):
    def __init__(self, columns, rows):
        sprite.Group.__init__(self)
        self.enemies = [[None] * columns for _ in range(rows)]
        self.columns = columns
        self.rows = rows
        self.leftAddMove = 0
        self.rightAddMove = 0
        self.moveTime = 600
        self.direction = 1
        self.rightMoves = 30
        self.leftMoves = 30
        self.moveNumber = 15
        self.timer = time.get_ticks()
        self.bottom = int((game.enemyPosition + ((rows - 1) * 45) + 35) * get_height_inc())
        self._aliveColumns = list(range(columns))
        self._leftAliveColumn = 0
        self._rightAliveColumn = columns - 1

    def update(self, current_time):
        if current_time - self.timer > self.moveTime:
            if self.direction == 1:
                max_move = self.rightMoves + self.rightAddMove
            else:
                max_move = self.leftMoves + self.leftAddMove

            if self.moveNumber >= max_move:
                self.leftMoves = 30 + self.rightAddMove
                self.rightMoves = 30 + self.leftAddMove
                self.direction *= -1
                self.moveNumber = 0
                self.bottom = 0
                for enemy in self:
                    enemy.rect.y += ENEMY_MOVE_DOWN
                    enemy.toggle_image()
                    if self.bottom < enemy.rect.y + 35:
                        self.bottom = enemy.rect.y + 35
            else:
                velocity = 10 if self.direction == 1 else -10
                for enemy in self:
                    enemy.rect.x += velocity
                    enemy.toggle_image()
                self.moveNumber += 1

            self.timer += self.moveTime

    def add_internal(self, *sprites):
        super(EnemiesGroup, self).add_internal(*sprites)
        for s in sprites:
            self.enemies[s.row][s.column] = s

    def remove_internal(self, *sprites):
        super(EnemiesGroup, self).remove_internal(*sprites)
        for s in sprites:
            self.kill(s)
        self.update_speed()

    def is_column_dead(self, column):
        return not any(self.enemies[row][column]
                       for row in range(self.rows))

    def random_bottom(self):
        col = choice(self._aliveColumns)
        col_enemies = (self.enemies[row - 1][col]
                       for row in range(self.rows, 0, -1))
        return next((en for en in col_enemies if en is not None), None)

    def update_speed(self):
        if len(self) == 1:
            self.moveTime = 200
        elif len(self) <= 10:
            self.moveTime = 400

    def kill(self, enemy):
        self.enemies[enemy.row][enemy.column] = None
        is_column_dead = self.is_column_dead(enemy.column)
        if is_column_dead:
            self._aliveColumns.remove(enemy.column)

        if enemy.column == self._rightAliveColumn:
            while self._rightAliveColumn > 0 and is_column_dead:
                self._rightAliveColumn -= 1
                self.rightAddMove += 5
                is_column_dead = self.is_column_dead(self._rightAliveColumn)

        elif enemy.column == self._leftAliveColumn:
            while self._leftAliveColumn < self.columns and is_column_dead:
                self._leftAliveColumn += 1
                self.leftAddMove += 5
                is_column_dead = self.is_column_dead(self._leftAliveColumn)


class Blocker(sprite.Sprite):
    def __init__(self, size, color, row, column):
        sprite.Sprite.__init__(self)
        self.height = size * get_height_inc()
        self.width = size * get_width_inc()
        self.color = color
        self.image = Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.row = row
        self.column = column

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)


class Mystery(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['mystery']
        self.image = transform.scale(self.image, (75, 35))
        self.rect = self.image.get_rect(topleft=(-80, 45))
        self.row = 5
        self.moveTime = 25000
        self.direction = 1
        self.timer = time.get_ticks()

    def update(self, keys, currentTime, *args):
        resetTimer = False
        passed = currentTime - self.timer
        if passed > self.moveTime:
            if self.rect.x < 840 and self.direction == 1:
                self.rect.x += 2
                game.screen.blit(self.image, self.rect)
            if self.rect.x > -100 and self.direction == -1:
                self.rect.x -= 2
                game.screen.blit(self.image, self.rect)

        if self.rect.x > 830:
            self.direction = -1
            resetTimer = True
        if self.rect.x < -90:
            self.direction = 1
            resetTimer = True
        if passed > self.moveTime and resetTimer:
            self.timer = currentTime


class EnemyExplosion(sprite.Sprite):
    def __init__(self, enemy, *groups):
        super(EnemyExplosion, self).__init__(*groups)
        self.image = transform.scale(self.get_image(enemy.row), (40, 35))
        self.image2 = transform.scale(self.get_image(enemy.row), (50, 45))
        self.image, self.image2 = _scale_img(self.image), _scale_img(self.image2)
        self.rect = self.image.get_rect(topleft=(enemy.rect.x, enemy.rect.y))
        self.timer = time.get_ticks()

    @staticmethod
    def get_image(row):
        img_colors = ['purple', 'blue', 'blue', 'green', 'green']
        return IMAGES['explosion{}'.format(img_colors[row])]

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 100:
            game.screen.blit(self.image, self.rect)
        elif passed <= 200:
            game.screen.blit(self.image2, (self.rect.x - 6, self.rect.y - 6))
        elif 400 < passed:
            self.kill()


class MysteryExplosion(sprite.Sprite):
    def __init__(self, mystery, score, *groups):
        super(MysteryExplosion, self).__init__(*groups)
        self.text = Text(FONT, int(20 * get_height_inc()), str(score), WHITE,
                         mystery.rect.x + int(20 * get_width_inc()), mystery.rect.y + int(6 * get_height_inc()))
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 200 or 400 < passed <= 600:
            self.text.draw(game.screen)
        elif 600 < passed:
            self.kill()


class ShipExplosion(sprite.Sprite):
    def __init__(self, ship, *groups):
        super(ShipExplosion, self).__init__(*groups)
        self.image = IMAGES['ship']
        self.rect = self.image.get_rect(topleft=(ship.rect.x, ship.rect.y))
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if 300 < passed <= 600:
            game.screen.blit(self.image, self.rect)
        elif 900 < passed:
            self.kill()


class Life(sprite.Sprite):
    def __init__(self, xpos, ypos):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.image = transform.scale(self.image, (int(23 * get_width_inc()), int(23 * get_height_inc())))
        self.rect = self.image.get_rect(topleft=(int(xpos * get_width_inc()), int(ypos * get_height_inc())))

    def update(self, *args):
        game.screen.blit(self.image, self.rect)


class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, int(size * get_height_inc()))
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(int(xpos * get_width_inc()), int(ypos * get_height_inc())))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


#---------- MAC ENG ADDITIONS START -----------#
class TextVariableMsg(object):
    def __init__(self, textFont, size, color, xpos, ypos):
        self.font = textFont
        self.size = size
        self.color = color 
        self.xpos = xpos
        self.ypos = ypos 

    def create(self, message):
        return Text(self.font, self.size, message, self.color, self.xpos, self.ypos)

class TextVariableColor(object):
    def __init__(self, textFont, size, message, xpos, ypos):
        self.font = textFont
        self.size = size
        self.message = message 
        self.xpos = xpos
        self.ypos = ypos 

    def create(self, color):
        return Text(self.font, self.size, self.message, color, self.xpos, self.ypos)   

#---------- MAC ENG ADDITIONS END -------------#

def set_display_vals(height, width):
    environ['DISPLAY_HEIGHT'], environ['DISPLAY_WIDTH'] = str(height), str(width)

def get_height_inc():
    return int(environ['DISPLAY_HEIGHT']) / ORIGINAL_HEIGHT

def get_width_inc():
    return int(environ['DISPLAY_WIDTH']) / ORIGINAL_WIDTH


### ****************************************************** ####
### *************** maceng.receiver.py ******************* ####
### ****************************************************** ####

class Receiver:
    @staticmethod
    def gameover(form_data):
        logging.debug("Gameover signal received. Form data: \n{}".format(form_data))
        Score.add_score(
            username=form_data["username"], 
            score=form_data["score"],
            )

### ****************************************************** ####
### ******************* form_screen.py ******************* ####
### ****************************************************** ####

class EnterTextInput:
    text = ""
    active = False 

    def __init__(self, label, screen, background, ypos):
        self.label = label
        self.screen = screen
        self.background = background
        self.ypos = ypos

    def create(self):
        logging.debug("Creating input {}".format(self.label))

        self.label_text = Text(
            textFont=FONT, 
            size=40, 
            color=GREEN,
            message="ENTER " + self.label + ":", 
            xpos=170, 
            ypos=self.ypos
        )
        self.label_text.draw(self.screen)

        self.input_text = TextVariableMsg(
            textFont=FONT, 
            size=40, 
            color=YELLOW,
            xpos=170, 
            ypos=self.ypos + 50
        )
        self.input_text.create(self._cursor).draw(self.screen)

    @property
    def _cursor(self):
        return "|" if self.active else ""
    
    def draw(self):
        self.label_text.draw(self.screen)
        self.input_text.create(self.text + self._cursor).draw(self.screen)

    def update(self, key):
        logging.debug("Key pressed: {}".format(key))

        if ((key >= K_a and key <= K_z) 
            or (key >= K_0 and key <= K_9)):
            self.text += chr(key)
            self.draw()
        elif (key == K_BACKSPACE):
            self.text = self.text[:-1]
            self.draw()
        elif (key == K_RETURN):
            if self.text != "":
                self.active = False 
                return self.text, True 
        
        return self.text, False 

    def reset(self):
        self.text = ""

FORM_LABELS = [
    "username",
]

class FormScreensController:

    def __init__(self, screen, background):
        self.screen = screen
        self.background = background

        self.forms = {}
        ypos = 50
        for l in FORM_LABELS:
            self.forms[l] = EnterTextInput(l, screen, background, ypos)
            ypos += 120

        self.form_data = {}.fromkeys(self.forms.keys(), "")
        self.current_form = self.forms[FORM_LABELS[0]]
        self.current_form.active = True 

        self.created = False 

    def create(self):
        if not self.created:
            self.screen.blit(self.background, (0, 0))
            for label, form in self.forms.items():
                form.create()
            self.created = True

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for label, form in self.forms.items():
            form.draw()

    def update(self, key):
        text, done = self.current_form.update(key) 

        if done:
            self.form_data[self.current_form.label] = text

            # go to the next form if there is a next form
            i = FORM_LABELS.index(self.current_form.label)
            if (i < len(FORM_LABELS)-1):
                self.current_form = self.forms[FORM_LABELS[i+1]]
                self.current_form.active = True 
                self.draw()
            else:
                return self.form_data, True 
        else:
            self.draw()

        return self.form_data, False 

    def reset(self):
        for k, v in self.forms.items():
            v.reset()
        self.current_form = self.forms[FORM_LABELS[0]]
        self.form_data = {}.fromkeys(self.forms.keys(), "")
        self.created = False 

### ****************************************************** ####
### ******************* leaderboard.py ******************* ####
### ****************************************************** ####

# constants
BTN_LABEL_SIZE = 25
BTN_COLOR_IDLE = WHITE
BTN_COLOR_ACTIVE = YELLOW
BTN_COLOR_DISABLED = GRAY
TABLE_TXT_SIZE = 20
TABLE_HDR_COLOR = PURPLE
TABLE_TXT_COLOR = BLUE

class Button(object):

    def __init__(self, label, xpos, ypos, active=False, disabled=False):
        self.label = label
        self.active = active
        self.disabled = disabled
        self.xpos = xpos
        self.ypos = ypos

    def initialize(self):
        self.text = TextVariableColor(
            textFont=FONT, 
            size=BTN_LABEL_SIZE, 
            message=self.label, 
            xpos=self.xpos, 
            ypos=self.ypos
        )       

class Page(object):

    def __init__(self, title, subtitle=None, active=False):
        self.title = title
        self.subtitle = subtitle
        self.active = active
        self.table = None

    def initialize(self):
        self.title_text = Text(
            textFont=FONT, 
            size=50, 
            color=GREEN,
            message=self.title, 
            xpos=170, 
            ypos=7
        )
        if self.subtitle:
            self.subtitle_text = Text(
                textFont=FONT, 
                size=23, 
                color=WHITE,
                message=self.subtitle, 
                xpos=280, 
                ypos=60
            )

    def create_title_texts(self, screen):
        self.title_text.draw(screen)
        if self.subtitle:
            self.subtitle_text.draw(screen) 

    def create_table(self, screen, data):
        # creates a table given data.
        # the data should be a list of rows for the table.
        num_cols = len(data[0])
        num_rows = len(data)
        xstart = 50
        xend = 800
        ystart = 100
        yend = 660

        xinc = (xend - xstart) / num_cols
        yinc = 24

        # store all texts into a big array
        self.table = []

        # top row
        for col in range(num_cols):
            xpos = xstart + col * xinc
            ypos = ystart
            self.table.append(Text(
                textFont=FONT, 
                size=TABLE_TXT_SIZE, 
                color=TABLE_HDR_COLOR,
                message=data[0][col], 
                xpos=xpos, 
                ypos=ypos
            ))

        # all other rows
        for row in range(1, num_rows):
            for col in range(num_cols):
                xpos = xstart + col * xinc
                ypos = ystart + row * yinc
                self.table.append(Text(
                    textFont=FONT, 
                    size=TABLE_TXT_SIZE, 
                    color=TABLE_TXT_COLOR,
                    message=data[row][col], 
                    xpos=xpos, 
                    ypos=ypos
                ))  

class Leaderboard(object):

    def __init__(self, screen, background):
        self.screen = screen 
        self.background = background
        self.active_index = 1

    def initialize(self):
        for p in PAGES:
            p.initialize()
        for b in BUTTONS:
            b.initialize()

        alltime_scores = Score.get_top_scores()
        logging.debug("All-time scores: \n{}".format(alltime_scores))

        alltime_table = [["Rank", "Username", "Score"]]
        rank = 1
        for score in alltime_scores:
            alltime_table.append([
                str(f'{rank:02}'), 
                score.user.username, 
                str(score.score)
            ])
            rank += 1

        ALLTIME_PG.create_table(self.screen, alltime_table)


    def create(self):
        self.screen.blit(self.background, (0, 0))

        # draw title text
        PAGES[self.active_index].create_title_texts(self.screen)

        # draw menu buttons
        for b in BUTTONS:
            if (b.active):
                b.text.create(BTN_COLOR_ACTIVE).draw(self.screen)
            elif (b.disabled):
                b.text.create(BTN_COLOR_DISABLED).draw(self.screen)
            else:
                b.text.create(BTN_COLOR_IDLE).draw(self.screen)

        # draw table if applicable 
        if PAGES[self.active_index].table is not None:
            for t in PAGES[self.active_index].table:
                t.draw(self.screen)


    def _inc_active_btn(self):
        original_index = self.active_index
        new_index = original_index + 1
        while (new_index < len(BUTTONS) and BUTTONS[new_index].disabled):
            new_index += 1
        if (new_index < len(BUTTONS) and not BUTTONS[new_index].disabled):
            self.active_index = new_index
            BUTTONS[new_index].active = True 
            BUTTONS[original_index].active = False

    def _dec_active_btn(self):
        original_index = self.active_index
        new_index = original_index - 1
        while (new_index >= 0 and BUTTONS[new_index].disabled):
            new_index -= 1
        if (new_index >= 0 and not BUTTONS[new_index].disabled):
            self.active_index = new_index
            BUTTONS[new_index].active = True 
            BUTTONS[original_index].active = False      

    def update(self, key_press):
        if (key_press == K_RIGHT):
            logging.debug("right key pressed")
            self._inc_active_btn()
        elif (key_press == K_LEFT):
            logging.debug("left key pressed")
            self._dec_active_btn()
        elif (key_press == K_RETURN):
            logging.debug("return key pressed on menu button \"{}\"".format(BUTTONS[self.active_index].label))
            if (BUTTONS[self.active_index] == MAIN_MENU):
                return True 
        return False 

BUTTONS = [
    Button("Main menu", 100, 560),
    Button("All-time",300, 560, active=True),
    Button("Credits", 600, 560),
]
MAIN_MENU = BUTTONS[0]

# pages 
ALLTIME_PG = Page("Leaderboard", subtitle="All-time", active=True)

PAGES = [
    ALLTIME_PG,
    ALLTIME_PG, 
    Page("Credits"),
]

### ****************************************************** ####
### ******************* models.py ************************ ####
### ****************************************************** ####

class User:

    username = None

    def __init__(self, username):
        self.username = username

    def __str__(self):
        return self.username
    
class Score:

    score = None
    user = None

    def __init__(self, score, username):
        self.score = score
        self.user = User(username)

    def __str__(self):
        return "{score} [{username}]".format(score=self.score, username=self.user.username)

    @classmethod
    def get_top_scores(cls):
        # return list of top scores from text file
        # return [Score(100, 'areeba'), Score(0, 'maanav'), Score(33, 'lafod')]
        try:
            file = open("scores", "r")
        except:
            f = open("scores", "w")
            f.close()
            return []

        raw_scores = file.readlines()
        scores = []
        for s in raw_scores:
            ss = s.strip().split(" ")
            scores.append(Score(ss[1], ss[0]))

        return scores

    @classmethod
    def add_score(cls, username, score):
        # TODO: add this new score to the csv file
        pass 

###################### SPACEINVADERS ##############################
class SpaceInvaders(object):
    def __init__(self):
        global BLOCKERS_POSITION, ENEMY_DEFAULT_POSITION, ENEMY_MOVE_DOWN
        # It seems, in Linux buffersize=512 is not enough, use 4096 to prevent:
        #   ALSA lib pcm.c:7963:(snd_pcm_recover) underrun occurred
        init()

        #---------- MAC ENG ADDITIONS START -----------#
        # get the new fullscreen width and height and calculate ratio based on the original game's dimensions
        display_info = display.Info() 
        screen_width, screen_height = display_info.current_w, display_info.current_h

        logging.debug("Screen width = {}, Screen height = {}".format(screen_width, screen_height))
        set_display_vals(screen_height, screen_width)
        logging.debug("Width increase ratio = {}, Height increase ratio = {}".format(get_width_inc(), get_height_inc()))

        BLOCKERS_POSITION = int(BLOCKERS_POSITION * get_height_inc())
        ENEMY_DEFAULT_POSITION = int(ENEMY_DEFAULT_POSITION * get_height_inc())
        ENEMY_MOVE_DOWN = int(ENEMY_MOVE_DOWN * get_height_inc())

        #---------- MAC ENG ADDITIONS END -------------#

        self.clock = time.Clock()
        self.caption = display.set_caption('Space Invaders')
        self.screen = SCREEN
        self.background = image.load(IMAGE_PATH + 'background.jpg').convert()
        self.background = transform.scale(self.background, (screen_width, screen_height))
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        # Counter for enemy starting position (increased each new round)
        self.enemyPosition = ENEMY_DEFAULT_POSITION
        self.titleText = Text(FONT, 50, 'Space Invaders', WHITE, 164, 155)
        self.titleText2 = Text(FONT, 25, 'Press any key to continue', WHITE,
                               201, 225)
        self.gameOverText = Text(FONT, 50, 'Game Over', WHITE, 250, 270)
        self.nextRoundText = Text(FONT, 50, 'Next Round', WHITE, 240, 270)
        self.enemy1Text = Text(FONT, 25, '   =   10 pts', GREEN, 368, 270)
        self.enemy2Text = Text(FONT, 25, '   =  20 pts', BLUE, 368, 320)
        self.enemy3Text = Text(FONT, 25, '   =  30 pts', PURPLE, 368, 370)
        self.enemy4Text = Text(FONT, 25, '   =  ?????', RED, 368, 420)
        self.scoreText = Text(FONT, 20, 'Score', WHITE, 5, 5)
        self.livesText = Text(FONT, 20, 'Lives ', WHITE, 640, 5)

        self.life1 = Life(715, 3)
        self.life2 = Life(742, 3)
        self.life3 = Life(769, 3)
        self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)

        #---------- MAC ENG ADDITIONS START -----------#
        # gameover
        self.gameover_signal = False 
        self.gameOverText_scoreV = TextVariableMsg(FONT, 30, BLUE, 320, 330)

        # leaderboard
        self.leaderboardScreen = False
        self.leaderboard = Leaderboard(self.screen, self.background)
        self.leaderboardInitialized = False 

        # enter username
        self.formActive = False 
        self.formScreens = FormScreensController(self.screen, self.background)

        #---------- MAC ENG ADDITIONS END -------------#

    def reset(self, score):
        self.player = Ship()
        self.playerGroup = sprite.Group(self.player)
        self.explosionsGroup = sprite.Group()
        self.bullets = sprite.Group()
        self.mysteryShip = Mystery()
        self.mysteryGroup = sprite.Group(self.mysteryShip)
        self.enemyBullets = sprite.Group()
        self.make_enemies()
        self.allSprites = sprite.Group(self.player, self.enemies,
                                       self.livesGroup, self.mysteryShip)
        self.keys = key.get_pressed()

        self.timer = time.get_ticks()
        self.noteTimer = time.get_ticks()
        self.shipTimer = time.get_ticks()
        self.score = score
        self.makeNewShip = False
        self.shipAlive = True

    def make_blockers(self, number):
        blockerGroup = sprite.Group()
        for row in range(4):
            for column in range(9):
                blocker = Blocker(10, GREEN, row, column)
                blocker.rect.x = int(50 * get_width_inc()) + (int(200 * get_width_inc()) * number) + (column * blocker.width)
                blocker.rect.y = BLOCKERS_POSITION + (row * blocker.height)
                blockerGroup.add(blocker)
        return blockerGroup

    @staticmethod
    def should_exit(evt):
        # type: (pygame.event.EventType) -> bool
        return evt.type == QUIT or (evt.type == KEYUP and evt.key == K_ESCAPE)

    def check_input(self):
        self.keys = key.get_pressed()
        for e in event.get():
            if self.should_exit(e):
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    if len(self.bullets) == 0 and self.shipAlive:
                        if self.score < 1000:
                            bullet = Bullet(self.player.rect.x + 23,
                                            self.player.rect.y + 5, -1,
                                            15, 'laser', 'center')
                            self.bullets.add(bullet)
                            self.allSprites.add(self.bullets)
                        else:
                            leftbullet = Bullet(self.player.rect.x + 8,
                                                self.player.rect.y + 5, -1,
                                                15, 'laser', 'left')
                            rightbullet = Bullet(self.player.rect.x + 38,
                                                 self.player.rect.y + 5, -1,
                                                 15, 'laser', 'right')
                            self.bullets.add(leftbullet)
                            self.bullets.add(rightbullet)
                            self.allSprites.add(self.bullets)

    def make_enemies(self):
        enemies = EnemiesGroup(10, 5)
        for row in range(5):
            for column in range(10):
                enemy = Enemy(row, column)
                enemy.rect.x = int(157 * get_width_inc()) + (column * int(50 * get_width_inc()))
                enemy.rect.y = self.enemyPosition + (row * int(45 * get_height_inc()))
                enemies.add(enemy)

        self.enemies = enemies

    def make_enemies_shoot(self):
        if (time.get_ticks() - self.timer) > 700 and self.enemies:
            enemy = self.enemies.random_bottom()
            self.enemyBullets.add(
                Bullet(enemy.rect.x + 14, enemy.rect.y + 20, 1, 5,
                       'enemylaser', 'center'))
            self.allSprites.add(self.enemyBullets)
            self.timer = time.get_ticks()

    def calculate_score(self, row):
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 300])
                  }

        score = scores[row]
        self.score += score
        return score

    def create_main_menu(self):
        self.enemy1 = IMAGES['enemy3_1']
        self.enemy1 = transform.scale(self.enemy1, (40, 40))
        self.enemy1 = _scale_img(self.enemy1)
        self.enemy2 = IMAGES['enemy2_2']
        self.enemy2 = transform.scale(self.enemy2, (40, 40))
        self.enemy2 = _scale_img(self.enemy2)
        self.enemy3 = IMAGES['enemy1_2']
        self.enemy3 = transform.scale(self.enemy3, (40, 40))
        self.enemy3 = _scale_img(self.enemy3)
        self.enemy4 = IMAGES['mystery']
        self.enemy4 = transform.scale(self.enemy4, (80, 40))
        self.enemy4 = _scale_img(self.enemy4)
        self.screen.blit(self.enemy1, (int(318 * get_width_inc()), int(270 * get_height_inc())))
        self.screen.blit(self.enemy2, (int(318 * get_width_inc()), int(320 * get_height_inc())))
        self.screen.blit(self.enemy3, (int(318 * get_width_inc()), int(370 * get_height_inc())))
        self.screen.blit(self.enemy4, (int(299 * get_width_inc()), int(420 * get_height_inc())))

    def check_collisions(self):
        sprite.groupcollide(self.bullets, self.enemyBullets, True, True)

        for enemy in sprite.groupcollide(self.enemies, self.bullets,
                                         True, True).keys():
            self.calculate_score(enemy.row)
            EnemyExplosion(enemy, self.explosionsGroup)
            self.gameTimer = time.get_ticks()

        for mystery in sprite.groupcollide(self.mysteryGroup, self.bullets,
                                           True, True).keys():
            score = self.calculate_score(mystery.row)
            MysteryExplosion(mystery, score, self.explosionsGroup)
            newShip = Mystery()
            self.allSprites.add(newShip)
            self.mysteryGroup.add(newShip)

        for player in sprite.groupcollide(self.playerGroup, self.enemyBullets,
                                          True, True).keys():
            logging.debug("Collision with player.")
            if self.life3.alive():
                self.life3.kill()
            elif self.life2.alive():
                self.life2.kill()
            elif self.life1.alive():
                self.life1.kill()
                self.gameOver = True
                self.startGame = False
            ShipExplosion(player, self.explosionsGroup)
            self.makeNewShip = True
            self.shipTimer = time.get_ticks()
            self.shipAlive = False

        if self.enemies.bottom >= int(540 * get_height_inc()):
            sprite.groupcollide(self.enemies, self.playerGroup, True, True)
            player_alive = self.player.alive()
            if not player_alive or self.enemies.bottom >= int(600 * get_height_inc()):
                self.gameOver = True
                self.startGame = False
            logging.debug("self.gameover = {}".format(self.gameOver))

        sprite.groupcollide(self.bullets, self.allBlockers, True, True)
        sprite.groupcollide(self.enemyBullets, self.allBlockers, True, True)
        if self.enemies.bottom >= BLOCKERS_POSITION:
            sprite.groupcollide(self.enemies, self.allBlockers, False, True)

    def create_new_ship(self, createShip, currentTime):
        if createShip and (currentTime - self.shipTimer > 900):
            self.player = Ship()
            self.allSprites.add(self.player)
            self.playerGroup.add(self.player)
            self.makeNewShip = False
            self.shipAlive = True

    def create_game_over(self, currentTime, score):
        self.screen.blit(self.background, (0, 0))
        self.gameOverText_score = self.gameOverText_scoreV.create("Score: {}".format(score))

        passed = currentTime - self.timer
        if passed < 750:
            # SHOW SCORE
            self.gameOverText.draw(self.screen)
            self.gameOverText_score.draw(self.screen)
        elif 750 < passed < 1500:
            # HIDE SCORE
            self.screen.blit(self.background, (0, 0))
        elif 1500 < passed < 2250:
            # SHOW SCORE
            self.gameOverText.draw(self.screen)
            self.gameOverText_score.draw(self.screen)
        elif 2250 < passed < 3000:
            # HIDE SCORE
            self.screen.blit(self.background, (0, 0))
        elif passed >= 3000:
            #---------- MAC ENG ADDITIONS START -----------#
            self.formActive = True
            self.gameOver = False 
            #---------- MAC ENG ADDITIONS END -----------#

        for e in event.get():
            if self.should_exit(e):
                sys.exit()

    def main(self):
        while True:
            if self.mainScreen:
                self.screen.blit(self.background, (0, 0))
                self.titleText.draw(self.screen)
                self.titleText2.draw(self.screen)
                self.enemy1Text.draw(self.screen)
                self.enemy2Text.draw(self.screen)
                self.enemy3Text.draw(self.screen)
                self.enemy4Text.draw(self.screen)
                self.create_main_menu()
                for e in event.get():
                    if self.should_exit(e):
                        sys.exit()
                    if e.type == KEYDOWN:
                        # Only create blockers on a new game, not a new round
                        self.allBlockers = sprite.Group(self.make_blockers(0),
                                                        self.make_blockers(1),
                                                        self.make_blockers(2),
                                                        self.make_blockers(3))
                        self.livesGroup.add(self.life1, self.life2, self.life3)
                        self.reset(0)

                        ## UNCOMMENT FOR ACTUAL GAME ##

                        self.startGame = True 
                        self.leaderboardScreen = False

                        ## UNCOMMENT TO SKIP GAMEPLAY ##

                        # self.startGame = False 
                        # self.leaderboardScreen = True

                        ## END ##

                        self.mainScreen = False

                # reset signals for maceng_receiver
                self.gameover_signal = False 

            elif self.startGame:
                if not self.enemies and not self.explosionsGroup:
                    currentTime = time.get_ticks()
                    if currentTime - self.gameTimer < 3000:
                        self.screen.blit(self.background, (0, 0))
                        self.scoreText2 = Text(FONT, 20, str(self.score),
                                               GREEN, 85, 5)
                        self.scoreText.draw(self.screen)
                        self.scoreText2.draw(self.screen)
                        self.nextRoundText.draw(self.screen)
                        self.livesText.draw(self.screen)
                        self.livesGroup.update()
                        self.check_input()
                    if currentTime - self.gameTimer > 3000:
                        # Move enemies closer to bottom
                        self.enemyPosition += ENEMY_MOVE_DOWN
                        self.reset(self.score)
                        self.gameTimer += 3000
                else:
                    currentTime = time.get_ticks()
                    self.screen.blit(self.background, (0, 0))
                    self.allBlockers.update(self.screen)
                    self.scoreText2 = Text(FONT, 20, str(self.score), GREEN,
                                           85, 5)
                    self.scoreText.draw(self.screen)
                    self.scoreText2.draw(self.screen)
                    self.livesText.draw(self.screen)
                    self.check_input()
                    self.enemies.update(currentTime)
                    self.allSprites.update(self.keys, currentTime)
                    self.explosionsGroup.update(currentTime)
                    self.check_collisions()
                    self.create_new_ship(self.makeNewShip, currentTime)
                    self.make_enemies_shoot()

            elif self.gameOver:
                currentTime = time.get_ticks()
                # Reset enemy starting position
                self.enemyPosition = ENEMY_DEFAULT_POSITION
                self.create_game_over(currentTime, score=self.score)

            #---------- MAC ENG ADDITIONS START -----------#
            elif self.formActive:
                self.formScreens.create()
                for e in event.get():
                    if self.should_exit(e):
                        sys.exit()
                    if e.type == KEYDOWN:
                        form_data, goto_leaderboard = self.formScreens.update(e.key)
                        logging.debug("Form Data: \n{}".format(form_data))
                        if goto_leaderboard:
                            form_data["score"] = self.score
                            Receiver.gameover(form_data=form_data)
                            self.formActive = False
                            self.leaderboardScreen = True 
                            self.formScreens.reset()

            elif self.leaderboardScreen:
                if not self.leaderboardInitialized:
                    self.leaderboard.initialize()
                    self.leaderboardInitialized = True 
                self.leaderboard.create()
                for e in event.get():
                    if self.should_exit(e):
                        sys.exit()
                    if e.type == KEYDOWN:
                        change_to_mainscreen = self.leaderboard.update(e.key)
                        if change_to_mainscreen:
                            self.mainScreen = True 
                            self.leaderboardScreen = False 
                            self.leaderboardInitialized = False 

            #---------- MAC ENG ADDITIONS END -----------#
            display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    game = SpaceInvaders()
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
    game.main()
