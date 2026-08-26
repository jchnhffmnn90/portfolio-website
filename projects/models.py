from django.db import models
from django.utils.text import slugify


class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    github_url = models.URLField(max_length=255)
    homepage_url = models.URLField(max_length=255, blank=True)
    language = models.CharField(max_length=50, blank=True)
    topics = models.JSONField(default=list, blank=True)
    stars_count = models.PositiveIntegerField(default=0)
    forks_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    pushed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-stars_count", "-pushed_at", "name"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self) -> str:
        return str(self.name)

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = str(slugify(self.name))  # type: ignore[assignment]
        super().save(*args, **kwargs)

