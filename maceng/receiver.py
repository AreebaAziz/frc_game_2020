import logging
from .models import Score

def gameover(form_data):
	logging.debug("Gameover signal received. Form data: \n{}".format(form_data))
	Score.add_score(
		username=form_data["username"], 
		score=form_data["score"],
		)