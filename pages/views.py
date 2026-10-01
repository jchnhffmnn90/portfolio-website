import logging
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from pages.forms import ContactForm
from projects.models import Project

logger = logging.getLogger(__name__)


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

    def form_valid(self, form: ContactForm) -> HttpResponse:
        message_instance = form.save()

        # Optional notification email to site owner if configured
        notification_email = getattr(settings, "CONTACT_NOTIFICATION_EMAIL", None)
        if notification_email:
            try:
                send_mail(
                    subject=f"[Portfolio Contact] {message_instance.subject or 'Neue Nachricht'}",
                    message=(
                        f"Name: {message_instance.name}\n"
                        f"Email: {message_instance.email}\n"
                        f"Subject: {message_instance.subject}\n\n"
                        f"{message_instance.message}"
                    ),
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "webmaster@localhost"),
                    recipient_list=[notification_email],
                    fail_silently=True,
                )
            except Exception as err:
                logger.warning("Could not dispatch contact email notification: %s", err)

        messages.success(
            self.request,
            _(
                "Vielen Dank! Deine Nachricht wurde erfolgreich übermittelt. "
                "Ich melde mich in Kürze bei dir."
            ),
        )
        return super().form_valid(form)
