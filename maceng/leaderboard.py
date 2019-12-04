import logging
from pygame import K_RIGHT, K_LEFT, K_RETURN
from .constants import * 

# constants
TITLE_SIZE = 50
TITLE_COLOR = GREEN
BTN_LABEL_SIZE = 25
BTN_COLOR_IDLE = WHITE
BTN_COLOR_ACTIVE = YELLOW
BTN_COLOR_DISABLED = GRAY

# NOTE - Button active and Page active are NOT the same thing!! #

class Button(object):

	def __init__(self, label, xpos, ypos, active=False, disabled=False):
		self.label = label
		self.active = active
		self.disabled = disabled
		self.xpos = xpos
		self.ypos = ypos

	def initialize(self):
		# need to do the import here to avoid cyclic import issue
		from spaceinvaders import TextVariableColor 
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

	def initialize(self):
		# need to do the import here to avoid cyclic import issue
		from spaceinvaders import Text 
		self.title_text = Text(
			textFont=FONT, 
			size=TITLE_SIZE, 
			color=TITLE_COLOR,
			message=self.title, 
			xpos=170, 
			ypos=7
		)

class Leaderboard(object):

	def __init__(self, screen, background):
		self.screen = screen 
		self.background = background
		self.active_page = PAGES[0]
		self.active_btn = BUTTONS[0]
		for p in PAGES:
			p.initialize()
		for b in BUTTONS:
			b.initialize()

	def create(self):
		self.screen.blit(self.background, (0, 0))

		# draw title text
		self.active_page.title_text.draw(self.screen)

		# draw menu buttons
		for b in BUTTONS:
			if (b.active):
				b.text.create(BTN_COLOR_ACTIVE).draw(self.screen)
			elif (b.disabled):
				b.text.create(BTN_COLOR_DISABLED).draw(self.screen)
			else:
				b.text.create(BTN_COLOR_IDLE).draw(self.screen)

	def _inc_active_btn(self):
		original_index = BUTTONS.index(self.active_btn)
		new_index = original_index + 1
		while (new_index < len(BUTTONS) and BUTTONS[new_index].disabled):
			new_index += 1
		if (new_index < len(BUTTONS) and not BUTTONS[new_index].disabled):
			self.active_btn = BUTTONS[new_index]
			BUTTONS[new_index].active = True 
			BUTTONS[original_index].active = False

	def _dec_active_btn(self):
		original_index = BUTTONS.index(self.active_btn)
		new_index = original_index - 1
		while (new_index >= 0 and BUTTONS[new_index].disabled):
			new_index -= 1
		if (new_index >= 0 and not BUTTONS[new_index].disabled):
			self.active_btn = BUTTONS[new_index]
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
			logging.debug("return key pressed on menu button \"{}\"".format(self.active_btn.label))
			if (self.active_btn == MAIN_MENU):
				return True 
		return False 

BUTTONS = [
	Button("Main menu", 30, 560, active=True),
	Button("Enter name", 240, 560),
	Button("Prev",500, 560, disabled=True),
	Button("Next", 590, 560),
]
MAIN_MENU = BUTTONS[0]

# pages 
PAGES = [
	Page("Leaderboard", subtitle="All-time", active=True),
	Page("Leaderboard", subtitle="Today"),
	Page("Credits"),
]