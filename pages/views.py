from typing import Any

from django.contrib import messages
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from pages.forms import ContactForm
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


class ContactView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("pages:contact")

    def form_valid(self, form: ContactForm):
        form.save()
        messages.success(
            self.request,
            _(
                "Vielen Dank! Deine Nachricht wurde erfolgreich übermittelt. "
                "Ich melde mich in Kürze bei dir."
            ),
        )
        return super().form_valid(form)
