from typing import Any

from django.db.models import QuerySet
from django.views.generic import TemplateView

from projects.models import Project


class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        visible_projects: QuerySet[Project] = Project.objects.filter(is_visible=True)

        featured_projects = list(visible_projects.filter(is_featured=True)[:6])
        if not featured_projects:
            featured_projects = list(visible_projects.order_by("-stars_count", "-pushed_at")[:6])

        context["featured_projects"] = featured_projects
        context["total_projects_count"] = visible_projects.count()
        return context
