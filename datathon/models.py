from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User

class Dataset(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name


class Level(models.Model):
	level = models.IntegerField()
	points = models.IntegerField()
	color = models.CharField(max_length=20)

	def __str__(self):
		return f'level {self.level}'


class Question(models.Model):
	level = models.ForeignKey(Level, on_delete=models.CASCADE)
	question = models.TextField()
	dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="questions")

	class Meta:
		ordering = ["level__level"]

	def __str__(self):
		return self.question


class Team(models.Model):
	name = models.CharField(max_length=100)
	points = models.DecimalField(decimal_places=1, max_digits=10 ,default=0)
	questions = models.ManyToManyField(Question, blank=True)
	bonus_points = models.IntegerField(default=0)
	saved_points = models.IntegerField(default=0)

	def __str__(self):
		return self.name

	def get_points(self):
		datasets = Dataset.objects.all()
		return sum([self.get_dataset_points(dataset.id) for dataset in datasets])

	def get_dataset_points(self, dataset_id):
		bonus_scores = self.bonus_scores.filter(dataset_id=dataset_id)
		points = sum(self.questions.all().filter(dataset_id=dataset_id).values_list('level__points', flat=True))
		if bonus_scores.exists():
			return points*0.6 + (float((self.bonus_scores.filter(dataset_id=dataset_id).aggregate(score=Avg('score'))['score']/5))*points*0.4)
		else:
			return points*0.6

	def is_dataset_done(self, dataset_id):
		solved_questions = self.questions.filter(dataset_id=dataset_id).count()
		dataset_questions = Question.objects.filter(dataset_id=dataset_id).count()
		return solved_questions==dataset_questions


class TeamDataset(models.Model):
	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="dataset_points")
	dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
	points = models.DecimalField(decimal_places=1, max_digits=10 ,default=0)

	class Meta:
		ordering = ["dataset"]


class BonusScore(models.Model):
	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="bonus_scores")
	dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="bonus_scores")
	score = models.DecimalField(decimal_places=1, max_digits=4 ,default=0)
	user = models.ForeignKey(User, on_delete=models.PROTECT)

	class Meta:
		unique_together = ['team', 'dataset', 'user']

