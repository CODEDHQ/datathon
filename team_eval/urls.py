"""team_eval URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('create/project/', create_project, name="create-project"),
    # path('projects/', projects_list, name="projects-list"),
    # path('project/<project_id>/', project_details, name="project-details"),
    # path('project/<project_id>/team/<team_id>/', team_project, name="team-project"),
    # path('feature/<feature_id>/team/<team_id>/', undo_feature, name="undo-feature"),
    # path('', teams, name="teams"),
    # path('x/', x),

    path('',include('datathon.urls')),
]

urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
