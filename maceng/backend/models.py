from django.db import models

class User(models.Model):

    username = models.CharField(max_length=10)
    frc_team = models.IntegerField()

    def __str__(self):
    	return self.username
    
class Score(models.Model):

	score = models.IntegerField()
	user = models.ForeignKey("User", on_delete=models.CASCADE)
	datetime = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "{score} [{user}]".format(score=self.score, user=self.user.username)

	@classmethod
	def get_alltime_scores(cls):
		return list(cls.objects.order_by('-score'))
