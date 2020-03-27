from django.db import models

class Dataset(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name


class Level(models.Model):
	level = models.IntegerField()
	points = models.IntegerField()

	def __str__(self):
		return f'level {self.level}'


class Question(models.Model):
	level = models.ForeignKey(Level, on_delete=models.CASCADE)
	question = models.TextField()
	dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="questions")
	prerequisites = models.ManyToManyField("Question", related_name="questions", blank=True)

	class Meta:
		ordering = ["level__level"]

	def __str__(self):
		return self.question


class Team(models.Model):
	name = models.CharField(max_length=100)
	points = models.IntegerField(default=0)
	questions = models.ManyToManyField(Question, blank=True)

	def __str__(self):
		return self.name

	def get_points(self):
		questions = self.questions.all()
		return sum([question.level.points for question in questions])

