import logging
from pygame import K_a, K_z, K_RETURN

class EnterNameScreen:

	username = ""

	def __init__(self, screen, background):
		self.screen = screen
		self.background = background

	def create(self):
		self.screen.blit(self.background, (0, 0))

	def update(self, key):
		logging.debug("Key pressed: {}".format(key))
		if (key >= K_a and key <= K_z):
			self.username += chr(key).upper()
			return self.username, False 
		elif (key == K_RETURN):
			return self.username, True 
		else:
			return self.username, False 

	def reset(self):
		self.username = ""
