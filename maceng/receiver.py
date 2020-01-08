import logging

def gameover(score: int, username:str):
	logging.info("Gameover signal received. Score: {}, Username: {}".format(score, username))