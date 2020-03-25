import logging

class User:

    username = None

    def __init__(self, username):
        self.username = username

    def __str__(self):
    	return self.username
    
class Score:

    score = None
    user = None

    def __init__(self, score, username):
        self.score = score
        self.user = User(username)

    def __str__(self):
        return "{score} [{username}]".format(score=self.score, username=self.user.username)

    @classmethod
    def get_top_scores(cls):
        # TODO: return list of top scores from csv file
        return [Score(100, 'areeba'), Score(0, 'maanav'), Score(33, 'lafod')]

    @classmethod
    def add_score(cls, username, score):
        # TODO: add this new score to the csv file
        pass 
