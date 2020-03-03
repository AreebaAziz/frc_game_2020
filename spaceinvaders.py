#!/usr/bin/env python

# Space Invaders
# Created by Lee Robinson

import logging
from pygame import *
import sys
from os.path import abspath, dirname
from os import environ
from random import choice
from maceng import receiver as maceng_receiver
from maceng.leaderboard import Leaderboard
from maceng.form_screen import FormScreensController
from maceng.constants import *
from maceng.joystick_interface import JoystickInterface

#SCREEN = display.set_mode((1280, 1024))
SCREEN = display.set_mode((0, 0), FULLSCREEN)
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
        global joystick_interface
        if (keys[K_LEFT] or joystick_interface.is_key_pressed(K_LEFT)) and self.rect.x > int(10 * get_width_inc()):
            self.rect.x -= self.speed
        if (keys[K_RIGHT] or joystick_interface.is_key_pressed(K_RIGHT)) and self.rect.x < int(740 * get_width_inc()):
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
        self.mysteryEntered = mixer.Sound(SOUND_PATH + 'mysteryentered.wav')
        self.mysteryEntered.set_volume(0.3)
        self.playSound = True

    def update(self, keys, currentTime, *args):
        resetTimer = False
        passed = currentTime - self.timer
        if passed > self.moveTime:
            if (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
                self.mysteryEntered.play()
                self.playSound = False
            if self.rect.x < 840 and self.direction == 1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x += 2
                game.screen.blit(self.image, self.rect)
            if self.rect.x > -100 and self.direction == -1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x -= 2
                game.screen.blit(self.image, self.rect)

        if self.rect.x > 830:
            self.playSound = True
            self.direction = -1
            resetTimer = True
        if self.rect.x < -90:
            self.playSound = True
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

class SpaceInvaders(object):
    def __init__(self):
        global BLOCKERS_POSITION, ENEMY_DEFAULT_POSITION, ENEMY_MOVE_DOWN, joystick_interface
        # It seems, in Linux buffersize=512 is not enough, use 4096 to prevent:
        #   ALSA lib pcm.c:7963:(snd_pcm_recover) underrun occurred
        mixer.pre_init(44100, -16, 1, 4096)
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
        self.caption = display.set_caption('The Last Defender')
        self.screen = SCREEN
        self.background = image.load(IMAGE_PATH + 'background.jpg').convert()
        self.background = transform.scale(self.background, (screen_width, screen_height))
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        # Counter for enemy starting position (increased each new round)
        self.enemyPosition = ENEMY_DEFAULT_POSITION
        self.titleText = Text(FONT, 50, 'The Last Defender', YELLOW, ORIGINAL_WIDTH*0.4, ORIGINAL_HEIGHT*0.4)
        self.titleText3 = Text(FONT, 25, 'A Fireball Story', YELLOW, 400, 210)
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

        # joystick interface
        joystick_interface = JoystickInterface(mapping={
            K_SPACE: 'round(joystick.get_button(2)) == 1',
            K_RIGHT: 'round(joystick.get_axis(1)) == 1',
            K_LEFT: 'round(joystick.get_axis(1)) == -1',
        })
        joystick_interface.init()

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
        self.create_audio()
        self.makeNewShip = False
        self.shipAlive = True

    def make_blockers(self, number):
        blockerGroup = sprite.Group()
        for row in range(4):
            for column in range(9):
                blocker = Blocker(10, FIREBALL, row, column)
                blocker.rect.x = int(50 * get_width_inc()) + (int(200 * get_width_inc()) * number) + (column * blocker.width)
                blocker.rect.y = BLOCKERS_POSITION + (row * blocker.height)
                blockerGroup.add(blocker)
        return blockerGroup

    def create_audio(self):
        self.sounds = {}
        for sound_name in ['shoot', 'shoot2', 'invaderkilled', 'mysterykilled',
                           'shipexplosion']:
            self.sounds[sound_name] = mixer.Sound(
                SOUND_PATH + '{}.wav'.format(sound_name))
            self.sounds[sound_name].set_volume(0.2)

        self.musicNotes = [mixer.Sound(SOUND_PATH + '{}.wav'.format(i)) for i
                           in range(4)]
        for sound in self.musicNotes:
            sound.set_volume(0.5)

        self.noteIndex = 0

    def play_main_music(self, currentTime):
        if currentTime - self.noteTimer > self.enemies.moveTime:
            self.note = self.musicNotes[self.noteIndex]
            if self.noteIndex < 3:
                self.noteIndex += 1
            else:
                self.noteIndex = 0

            self.note.play()
            self.noteTimer += self.enemies.moveTime

    @staticmethod
    def should_exit(evt):
        # type: (pygame.event.EventType) -> bool
        return evt.type == QUIT or (evt.type == KEYUP and evt.key == K_ESCAPE)

    def check_input(self):
        global joystick_interface
        self.keys = key.get_pressed()
        for e in event.get():
            if self.should_exit(e):
                sys.exit()
            if e.type == KEYDOWN or e.type == JOYBUTTONDOWN:
                if (hasattr(e, "key") and e.key == K_SPACE) or joystick_interface.is_key_pressed(K_SPACE):
                    if len(self.bullets) == 0 and self.shipAlive:
                        if self.score < 1000:
                            bullet = Bullet(self.player.rect.x + 23,
                                            self.player.rect.y + 5, -1,
                                            15, 'laser', 'center')
                            self.bullets.add(bullet)
                            self.allSprites.add(self.bullets)
                            self.sounds['shoot'].play()
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
                            self.sounds['shoot2'].play()

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
                Bullet(enemy.rect.x + int(18 * get_width_inc()), enemy.rect.y + int(25 * get_height_inc()), 1, 5,
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
            self.sounds['invaderkilled'].play()
            self.calculate_score(enemy.row)
            EnemyExplosion(enemy, self.explosionsGroup)
            self.gameTimer = time.get_ticks()

        for mystery in sprite.groupcollide(self.mysteryGroup, self.bullets,
                                           True, True).keys():
            mystery.mysteryEntered.stop()
            self.sounds['mysterykilled'].play()
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
            ######  COMMENT THIS FOR 1 LIFE DURING DEBUGGING #######
            # elif self.life2.alive():
            #     self.life2.kill()
            # elif self.life1.alive():
            #     self.life1.kill()
                self.gameOver = True
                self.startGame = False
            self.sounds['shipexplosion'].play()
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
                self.titleText3.draw(self.screen)
                self.titleText2.draw(self.screen)
                self.enemy1Text.draw(self.screen)
                self.enemy2Text.draw(self.screen)
                self.enemy3Text.draw(self.screen)
                self.enemy4Text.draw(self.screen)
                self.create_main_menu()
                for e in event.get():
                    if self.should_exit(e):
                        sys.exit()
                    if e.type == KEYDOWN or e.type == JOYBUTTONDOWN:
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
                    self.play_main_music(currentTime)
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
                            maceng_receiver.gameover(form_data=form_data)
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
                    if e.type == KEYDOWN or e.type == JOYBUTTONDOWN:
                        if e.type == JOYBUTTONDOWN:
                            equiv_key = joystick_interface.get_equiv_key()
                        else:
                            equiv_key = e.key 
                        change_to_mainscreen = self.leaderboard.update(equiv_key)
                        if change_to_mainscreen:
                            self.mainScreen = True 
                            self.leaderboardScreen = False 
                            self.leaderboardInitialized = False 

            #---------- MAC ENG ADDITIONS END -----------#
            display.update()
            self.clock.tick(45)


if __name__ == '__main__':
    game = SpaceInvaders()
    game.main()
