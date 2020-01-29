import logging
from pygame import K_RIGHT, K_LEFT, K_RETURN
from .constants import * 
from .backend.models import User, Score

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
		self.table = None

	def initialize(self):
		# need to do the import here to avoid cyclic import issue
		from spaceinvaders import Text 
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
		from spaceinvaders import Text 
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

		alltime_scores = Score.get_alltime_scores()
		logging.debug("All-time scores: \n{}".format(alltime_scores))

		alltime_table = [["Rank", "Username", "Team", "Score"]]
		rank = 1
		for score in alltime_scores:
			team = str(score.user.team) if score.user.team else "-"
			alltime_table.append([
				str(f'{rank:02}'), 
				score.user.username, 
				team, 
				str(score.score)
			])
			rank += 1

		ALLTIME_PG.create_table(self.screen, alltime_table)

		today_scores = Score.get_today_scores()
		logging.debug("Today scores: \n{}".format(today_scores))

		today_table = [["Rank", "Username", "Team", "Score"]]

		rank = 1
		for score in today_scores:
			team = str(score.user.team) if score.user.team else "-"
			today_table.append([
				str(f'{rank:02}'), 
				score.user.username, 
				team, 
				str(score.score)
			])
			rank += 1

		TODAY_PG.create_table(self.screen, today_table)


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
	Button("Today", 500, 560),
	Button("Credits", 600, 560),
]
MAIN_MENU = BUTTONS[0]

# pages 
ALLTIME_PG = Page("Leaderboard", subtitle="All-time", active=True)
TODAY_PG = Page("Leaderboard", subtitle="Today")

PAGES = [
	ALLTIME_PG,
	ALLTIME_PG, 
	TODAY_PG,
	Page("Credits"),
]
