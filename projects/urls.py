from django.urls import path

from projects.views import ProjectListView

app_name = "projects"

urlpatterns = [
    path("", ProjectListView.as_view(), name="list"),
]
