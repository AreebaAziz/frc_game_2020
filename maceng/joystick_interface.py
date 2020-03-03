import pygame
import logging

class JoystickInterface:

	'''
		mapping should be a dictionary containing pygame K_* to joystick values. 
		eg used in frc_game_2020:
		mapping = {
			K_SPACE: 'joystick.get_button(0) == 1',
			K_RIGHT: 'joystick.get_axis(0) == -1',
			K_LEFT: 'joystick.get_axis(0) == 1',
		}
	'''
	def __init__(self, mapping:dict=None):
		self.mapping = mapping
		self.joystick = None 
		for k, v in self.mapping.items():
			self.mapping[k] = v.split("==")[0].strip() + "==round(" + v.split("==")[1].strip() + ")"

	def init(self):
		# assumes up to 1 joystick set may be connected
		if pygame.joystick.get_count() == 1:
			logging.debug("Num joysticks detected: 1")
			self.joystick = pygame.joystick.Joystick(0)
			self.joystick.init()
		elif pygame.joystick.get_count() == 0:
			logging.debug("Num joysticks detected: 0")
			self.joystick = None 
		else:
			logging.debug("More than 1 joysticks detected. Only using the first one.")
			self.joystick = pygame.joystick.Joystick(0)
			self.joystick.init()

		# button
		self.num_buttons = self.joystick.get_numbuttons() if self.joystick is not None else 0
		logging.debug("Num buttons detected: {}".format(self.num_buttons))

	'''
		Returns the current values of the joystick's axes and buttons, as a pygame constant K_* that is 
		the functional equivalent. Eg. joystick axis 0 value of 1.00 will be returned as K_RIGHT. 
	'''
	def get_equiv_key(self):
		if self.joystick is None: return None 
		for k, c in self.mapping.items():
			if eval("self." + c):
				return k 

	def is_key_pressed(self, key):
		if self.joystick is None: 
			return None
		return eval("self." + self.mapping[key])
