from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataset, Team, Question, TeamDataset, BonusScore, Level
from django.http import JsonResponse
import requests

def teams(request):
	teams = Team.objects.all()
	if not request.user.is_authenticated and teams.first().saved_points > 0:
		teams = teams.order_by('-saved_points')

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
		"team_points": team.get_dataset_points(dataset_id),
		"done": team.is_dataset_done(dataset_id)
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


@login_required
def deactivate_dashboard(request):
	for team in Team.objects.all():
		team.saved_points = team.get_points()
		team.save()
		for dataset in Dataset.objects.all():
			dataset_points, created = TeamDataset.objects.get_or_create(team=team, dataset=dataset)
			dataset_points.points = team.get_dataset_points(dataset.id)
			dataset_points.save()
			
	return redirect("teams")


@login_required
def activate_dashboard(request):
	for team in Team.objects.all():
		team.saved_points = 0
		team.save()
		TeamDataset.objects.all().delete()

	return redirect("teams")


@login_required
def add_bonus_score(request, dataset_id, team_id):
	team = Team.objects.get(id=team_id)
	if request.method=="POST" and team.is_dataset_done(dataset_id):
		score = sum([float(score)for score in request.POST.getlist('score')])/3
		print(score)
		bonus_score, created = BonusScore.objects.get_or_create(team_id=team_id, dataset_id=dataset_id, user=request.user)
		bonus_score.score = score
		bonus_score.save()
	return redirect('team-dataset', dataset_id, team_id)


def add_datasets(request):
	if request.method == 'POST':
		board_id = request.POST['board_id']
		levels = {}
		for level in Level.objects.all():
			levels[f'L{level.level}'] = level 

		print(levels)

		url = "https://api.trello.com/1/boards/{board_id}/lists".format(board_id=board_id)
		querystring = {"fields":"name","cards":"all","card_fields":"name,labels", "key": "dd79278e4430052c1ed1ba5e53f086f0", "token": "db7e18f8ddb1ad6fad80d767c543c236e5c01080a6a28c37e606299f75a9ecac"}
		response = requests.request("GET", url, params=querystring)
		for dataset in response.json():
			dataset_obj = Dataset.objects.create(name=dataset["name"])
			for card in dataset["cards"]:
				if card["labels"]:
					Question.objects.create(level=levels[card["labels"][0]["name"]], dataset=dataset_obj, question=card["name"])
		return redirect("teams")
	return render(request, "create_project.html")
	
