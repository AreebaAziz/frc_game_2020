import logging
import pygame
from .constants import * 

class EnterTextScreen:
	text = ""

	def __init__(self, label, screen, background):
		self.label = label
		self.screen = screen
		self.background = background

	def create(self):
		# need to do the import here to avoid cyclic import issue
		from spaceinvaders import Text, TextVariableMsg

		self.screen.blit(self.background, (0, 0))
		logging.debug("On form {}".format(self.label))

		self.label_text = Text(
			textFont=FONT, 
			size=40, 
			color=GREEN,
			message="ENTER " + self.label + ":", 
			xpos=170, 
			ypos=50
		)
		self.label_text.draw(self.screen)

		self.input_text = TextVariableMsg(
			textFont=FONT, 
			size=40, 
			color=YELLOW,
			xpos=170, 
			ypos=100
		)
		self.input_text.create("|").draw(self.screen)

	def _update_display(self):
		self.screen.blit(self.background, (0, 0))
		self.label_text.draw(self.screen)
		self.input_text.create(self.text).draw(self.screen)

	def update(self, key):
		logging.debug("Key pressed: {}".format(key))
		mods = pygame.key.get_mods()

		if ((key >= pygame.K_a and key <= pygame.K_z) 
			or (key >= pygame.K_0 and key <= pygame.K_9)
			or (self.label == "email" and key == pygame.K_PERIOD)):

			# dumb code that lets you use @ and . symbol for email input 
			if (mods & pygame.KMOD_LSHIFT or mods & pygame.KMOD_CAPS or mods & pygame.KMOD_RSHIFT) and (key == pygame.K_2 and self.label == "email"):
				self.text += "@"
			else:
				self.text += chr(key)
			
			self._update_display()
		elif (key == pygame.K_BACKSPACE):
			self.text = self.text[:-1]
			self._update_display()
		elif (key == pygame.K_RETURN):
			if self.text != "":
				return self.text, True 
		
		return self.text, False 

	def reset(self):
		self.text = ""

FORM_LABELS = [
	"username",
	"email"
]

class FormScreensController:

	def __init__(self, screen, background):
		self.screen = screen
		self.background = background

		self.forms = {}
		for l in FORM_LABELS:
			self.forms[l] = EnterTextScreen(l, screen, background)

		self.form_data = {}.fromkeys(self.forms.keys(), "")
		self.current_form = self.forms[FORM_LABELS[0]]

		self.created = False 

	def create(self):
		if not self.created:
			self.current_form.create()
			self.created = True

	def update(self, key):
		text, done = self.current_form.update(key) 

		if done:
			self.form_data[self.current_form.label] = text

			# go to the next form if there is a next form
			i = FORM_LABELS.index(self.current_form.label)
			if (i < len(FORM_LABELS)-1):
				self.current_form = self.forms[FORM_LABELS[i+1]]
				self.current_form.create()
			else:
				return self.form_data, True 

		return self.form_data, False 

	def reset(self):
		for k, v in self.forms.items():
			v.reset()
		self.current_form = self.forms[FORM_LABELS[0]]
		self.form_data = {}.fromkeys(self.forms.keys(), "")
		self.created = False 