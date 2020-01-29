import logging
import pygame
from .constants import * 

class EnterTextInput:
	text = ""
	active = False 

	def __init__(self, label, screen, background, ypos):
		self.label = label
		self.screen = screen
		self.background = background
		self.ypos = ypos

	def create(self):
		# need to do the import here to avoid cyclic import issue
		from spaceinvaders import Text, TextVariableMsg

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
		mods = pygame.key.get_mods()

		if ((self.label != "team" and key >= pygame.K_a and key <= pygame.K_z) 
			or (key >= pygame.K_0 and key <= pygame.K_9)
			or (self.label == "email" and key == pygame.K_PERIOD)):

			# dumb code that lets you use @ and . symbol for email input 
			if (mods & pygame.KMOD_LSHIFT or mods & pygame.KMOD_CAPS or mods & pygame.KMOD_RSHIFT) and (key == pygame.K_2 and self.label == "email"):
				self.text += "@"
			else:
				self.text += chr(key)
			
			# self.draw()
		elif (key == pygame.K_BACKSPACE):
			self.text = self.text[:-1]
			# self.draw()
		elif (key == pygame.K_RETURN):
			if self.text != "":
				self.active = False 
				return self.text, True 
		
		return self.text, False 

	def reset(self):
		self.text = ""

FORM_LABELS = [
	"username",
	"email",
	"team"
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