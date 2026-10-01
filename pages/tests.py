import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from pages.models import ContactMessage
from projects.models import Project


@pytest.mark.django_db
def test_home_page_status_code_and_template(client):
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert "pages/home.html" in [t.name for t in response.templates]
    content = response.content.decode("utf-8")
    assert "Enterprise Application Integration Specialist" in content
    assert "Softwareentwickler ERP-Systeme" in content
    assert "Weiterbildung IT Administration & Automation" in content
    assert "Fachinformatiker Anwendungsentwicklung" in content
    assert "Bachelor Wirtschaftsinformatik" in content
    assert "IT-Systemelektroniker" in content
    assert "Ulm, Deutschland" in content


@pytest.mark.django_db
def test_home_page_displays_featured_projects(client):
    Project.objects.create(
        name="featured-one",
        github_url="https://github.com/testuser/featured-one",
        is_featured=True,
        is_visible=True,
    )
    Project.objects.create(
        name="normal-one",
        github_url="https://github.com/testuser/normal-one",
        is_featured=False,
        is_visible=True,
    )

    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert len(response.context["featured_projects"]) == 1
    assert response.context["featured_projects"][0].name == "featured-one"
    assert response.context["total_projects_count"] == 2


@pytest.mark.django_db
def test_home_page_fallback_top_starred(client):
    Project.objects.create(
        name="repo-star-5",
        github_url="https://github.com/testuser/repo-star-5",
        stars_count=5,
        is_featured=False,
        is_visible=True,
    )
    Project.objects.create(
        name="repo-star-10",
        github_url="https://github.com/testuser/repo-star-10",
        stars_count=10,
        is_featured=False,
        is_visible=True,
    )

    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert len(response.context["featured_projects"]) == 2
    assert response.context["featured_projects"][0].name == "repo-star-10"


@pytest.mark.django_db
def test_contact_page_get(client):
    response = client.get(reverse("pages:contact"))
    assert response.status_code == 200
    assert "pages/contact.html" in [t.name for t in response.templates]
    assert "form" in response.context


@pytest.mark.django_db
def test_contact_page_post_success(client):
    data = {
        "name": "Max Mustermann",
        "email": "max@example.com",
        "subject": "Projektanfrage Django",
        "message": "Hallo, ich würde gerne ein Projekt anfragen.",
        "honeypot": "",
    }
    response = client.post(reverse("pages:contact"), data=data, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [(reverse("pages:contact"), 302)]

    # Verify message in database
    message = ContactMessage.objects.first()
    assert message is not None
    assert message.name == "Max Mustermann"
    assert message.email == "max@example.com"
    assert message.subject == "Projektanfrage Django"
    assert message.message == "Hallo, ich würde gerne ein Projekt anfragen."
    assert not message.is_read

    # Verify flash message
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "erfolgreich übermittelt" in str(messages[0])


@pytest.mark.django_db
def test_contact_page_post_sends_notification_when_configured(client, settings):
    from django.core import mail

    settings.CONTACT_NOTIFICATION_EMAIL = "admin@example.com"
    data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "subject": "Collab",
        "message": "Let's work together!",
        "honeypot": "",
    }
    response = client.post(reverse("pages:contact"), data=data, follow=True)
    assert response.status_code == 200
    assert len(mail.outbox) == 1
    assert "admin@example.com" in mail.outbox[0].to
    assert "Collab" in mail.outbox[0].subject
    assert "Jane Doe" in mail.outbox[0].body


@pytest.mark.django_db
def test_contact_page_post_invalid(client):
    data = {
        "name": "",
        "email": "invalid-email",
        "subject": "",
        "message": "",
        "honeypot": "",
    }
    response = client.post(reverse("pages:contact"), data=data)
    assert response.status_code == 200
    assert ContactMessage.objects.count() == 0
    form = response.context["form"]
    assert not form.is_valid()
    assert "name" in form.errors
    assert "email" in form.errors
    assert "message" in form.errors


@pytest.mark.django_db
def test_contact_page_honeypot_spam_rejection(client):
    data = {
        "name": "Spam Bot",
        "email": "bot@spam.com",
        "subject": "Buy crypto",
        "message": "Spam message here",
        "honeypot": "I am a bot",
    }
    response = client.post(reverse("pages:contact"), data=data)
    assert response.status_code == 200
    assert ContactMessage.objects.count() == 0
    form = response.context["form"]
    assert not form.is_valid()
    assert "honeypot" in form.errors


@pytest.mark.django_db
def test_i18n_language_switching(client):
    # Default (German)
    res_de = client.get("/")
    assert res_de.status_code == 200
    assert "Projekte" in res_de.content.decode("utf-8")
    assert "Kontakt" in res_de.content.decode("utf-8")

    # English URL prefix (/en/)
    res_en = client.get("/en/")
    assert res_en.status_code == 200
    assert "Projects" in res_en.content.decode("utf-8")
    assert "Contact" in res_en.content.decode("utf-8")
    assert "Backend Development, System Integration & IT Automation." in res_en.content.decode(
        "utf-8"
    )
    assert "Professional Training: IT Administration & Automation" in res_en.content.decode("utf-8")


@pytest.mark.django_db
def test_i18n_set_language_view(client):
    post_res = client.post(
        reverse("set_language"),
        data={"language": "en", "next": "/"},
    )
    assert post_res.status_code == 302
    assert "django_language" in client.cookies
    assert client.cookies["django_language"].value == "en"
