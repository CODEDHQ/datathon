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

	class Meta:
		ordering = ["level__level"]

	def __str__(self):
		return self.question


class Team(models.Model):
	name = models.CharField(max_length=100)
	points = models.IntegerField(default=0)
	questions = models.ManyToManyField(Question, blank=True)
	bonus_points = models.IntegerField(default=0)
	saved_points = models.IntegerField(default=0)

	def __str__(self):
		return self.name

	def get_points(self):
		questions = self.questions.all()
		return sum([question.level.points for question in questions])

	def get_dataset_points(self, dataset_id):
		return sum(self.questions.all().filter(dataset_id=dataset_id).values_list('level__points', flat=True))


class TeamDataset(models.Model):
	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="dataset_points")
	dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
	points = models.IntegerField(default=0)

	class Meta:
		ordering = ["dataset"]





