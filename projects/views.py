from typing import Any

from django.db.models import Q, QuerySet
from django.views.generic import DetailView, ListView

from projects.models import Project


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self) -> QuerySet[Project]:
        queryset: QuerySet[Project] = Project.objects.filter(is_visible=True)

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(language__icontains=query)
            )

        language = self.request.GET.get("language", "").strip()
        if language:
            queryset = queryset.filter(language__iexact=language)

        topic = self.request.GET.get("topic", "").strip()
        if topic:
            queryset = queryset.filter(topics__contains=[topic])

        sort = self.request.GET.get("sort", "stars").strip()
        if sort == "recent":
            queryset = queryset.order_by("-pushed_at", "-stars_count")
        elif sort == "name":
            queryset = queryset.order_by("name")
        else:  # default 'stars'
            queryset = queryset.order_by("-stars_count", "-pushed_at")

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        all_visible = Project.objects.filter(is_visible=True)

        languages = (
            all_visible.exclude(language="")
            .values_list("language", flat=True)
            .distinct()
            .order_by("language")
        )

        all_topics: set[str] = set()
        for project in all_visible.only("topics"):
            if isinstance(project.topics, list):
                all_topics.update(project.topics)

        context["available_languages"] = list(languages)
        context["available_topics"] = sorted(all_topics)
        context["selected_language"] = self.request.GET.get("language", "").strip()
        context["selected_topic"] = self.request.GET.get("topic", "").strip()
        context["selected_sort"] = self.request.GET.get("sort", "stars").strip()
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "project"

    def get_queryset(self) -> QuerySet[Project]:
        return Project.objects.filter(is_visible=True)
