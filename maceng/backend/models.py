import logging
from django.utils import timezone
from django.db import models

class User(models.Model):

    username = models.CharField(max_length=10)
    frc_team = models.IntegerField(null=True, blank=True)

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

	@classmethod
	def get_today_scores(cls):
		return list(cls.objects.filter(datetime__gte=timezone.now().replace(hour=0, minute=0, second=0)).order_by('-score'))

	@classmethod
	def add_score(cls, username, score):
		logging.debug("Adding score {} by user {} to database.".format(score, username))
		user, created = User.objects.get_or_create(username=username[:12])
		cls.objects.create(score=score, user=user)
