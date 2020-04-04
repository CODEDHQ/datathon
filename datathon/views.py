from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataset, Team, Question, TeamDataset


def teams(request):
	teams = Team.objects.all()
	if request.user.is_authenticated:
		teams = teams.order_by('-points')
	else:
		if teams.first().saved_points:
			teams = teams.order_by('-saved_points')
		else:
			teams.order_by('-points')

	datasets = Dataset.objects.all()
	points_per_dataset = []
	for team in teams:
		team_points = [team.get_dataset_points(dataset.id) for dataset in datasets]
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
	level = 1

	levels = dataset.questions.order_by("-level__level").values_list('level__level', flat=True).distinct()
	for level in levels:
		finished_q = team.questions.filter(dataset=dataset, level__level=level).count()
		left_q = dataset.questions.filter(level__level=level).count()
		if finished_q == left_q:
			level = level+1
			break

	context = {
		"teams" : Team.objects.all(),
		"team" : team,
		"dataset" :  dataset,
		"level" : level,
		"team_points": sum(team.questions.filter(dataset_id=dataset_id).values_list('level__points', flat=True))
	}
	return render(request, 'team_project.html', context)


@login_required
def undo(request, team_id, question_id):
	team = Team.objects.get(id=team_id)
	question = Question.objects.get(id=question_id)
	team.questions.remove(question)
	questions = Question.objects.filter(level__level__gt=question.level.level)
	team.questions.remove(*questions)
	team.points = team.get_points()
	team.save()
	return redirect('team-dataset', question.dataset.id, team_id)


@login_required
def update(request, team_id, dataset_id):
	team = Team.objects.get(id=team_id)
	if request.method == 'POST':
		done = request.POST.getlist('question')
		for question in done:
			team.questions.add(question)
		team.points = team.get_points()
		team.save()
		return redirect('team-dataset', dataset_id, team_id)


def deactivate_dashboard(request):
	for team in Team.objects.all():
		team.saved_points = team.points
		team.save()
		for dataset in Dataset.objects.all():
			dataset_points, created = TeamDataset.objects.get_or_create(team=team, dataset=dataset)
			dataset_points.points = team.get_dataset_points(dataset.id)
			dataset_points.save()
			
	return redirect("teams")


def activate_dashboard(request):
	for team in Team.objects.all():
		team.saved_points = 0
		team.save()
		for dataset in Dataset.objects.all():
			dataset_points, created = TeamDataset.objects.get_or_create(team=team, dataset=dataset)
			dataset_points.points = 0
			dataset_points.save()
			
	return redirect("teams")



