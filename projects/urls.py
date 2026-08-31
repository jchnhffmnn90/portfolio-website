from django.urls import path

from projects.views import ProjectDetailView, ProjectListView

app_name = "projects"

urlpatterns = [
    path("", ProjectListView.as_view(), name="list"),
    path("<slug:slug>/", ProjectDetailView.as_view(), name="detail"),
]
