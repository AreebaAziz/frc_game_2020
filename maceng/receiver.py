import logging
from .backend.models import Score

def gameover(score: int, username:str):
	logging.info("Gameover signal received. Score: {}, Username: {}".format(score, username))
	Score.add_score(username=username, score=score)