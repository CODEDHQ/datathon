from django.urls import path
from .views import *

urlpatterns = [
    path('', teams, name="teams"),
    path('dataset/<dataset_id>/team/<team_id>/', team_dataset, name="team-dataset"),
    path('undo/question/<question_id>/team/<team_id>/', undo, name="undo"),
    path('update/team/<team_id>/dataset/<dataset_id>/', update, name="update"),
    path('deactivate/', deactivate_dashboard, name="deactivate-dashboard")

]