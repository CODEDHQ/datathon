from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataset, Team, Question


def teams(request):
	teams = Team.objects.all().order_by('-points')
	datasets = Dataset.objects.all()
	points_per_dataset = []
	for team in teams:
		team_points = [sum(team.questions.all().filter(dataset=dataset).values_list('level__points', flat=True)) for dataset in datasets]
		points_per_dataset.append(team_points)
	context = {
		"teams": teams,
		"datasets": datasets,
		"points_per_dataset":points_per_dataset
	}

	return render(request, 'teams.html', context)


@login_required
def team_dataset(request, dataset_id, team_id):
	dataset = Dataset.objects.get(id=dataset_id)
	team = Team.objects.get(id=team_id)

	locked = []
	for question in dataset.questions.all():
		if all(question in team.questions.all() for question in question.prerequisites.all()):
			locked.append(False)
		else:
			locked.append(True)

	context = {
		"teams" : Team.objects.all(),
		"team" : team,
		"dataset" :  dataset,
		"locked_questions" : locked,
		"team_points": sum(team.questions.filter(dataset_id=dataset_id).values_list('level__points', flat=True))
	}
	return render(request, 'team_project.html', context)


@login_required
def undo(request, team_id, question_id):
	team = Team.objects.get(id=team_id)
	question = Question.objects.get(id=question_id)
	team.questions.remove(question)
	return redirect('team-dataset', question.dataset.id, team_id)


@login_required
def update(request, team_id, dataset_id):
	team = Team.objects.get(id=team_id)
	if request.method == 'POST':
		done = request.POST.getlist('question')
		for question in done:
			team.questions.add(question)
		return redirect('team-dataset', dataset_id, team_id)


