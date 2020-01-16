import logging
from pygame import K_a, K_z, K_RETURN

class EnterTextScreen:
	text = ""

	def __init__(self, label, screen, background):
		self.label = label
		self.screen = screen
		self.background = background

	def create(self):
		self.screen.blit(self.background, (0, 0))
		logging.debug("On form {}".format(self.label))

	def update(self, key):
		logging.debug("Key pressed: {}".format(key))
		if (key >= K_a and key <= K_z):
			self.text += chr(key).upper()
			return self.text, False 
		elif (key == K_RETURN):
			return self.text, True 
		else:
			return self.text, False 

	def reset(self):
		self.text = ""

FORM_LABELS = [
	"username"
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