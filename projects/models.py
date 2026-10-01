from typing import Any

from django.db import models
from django.utils.text import slugify


class Project(models.Model):
    objects = models.Manager()

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    github_url = models.URLField(max_length=255)
    homepage_url = models.URLField(max_length=255, blank=True)
    language = models.CharField(max_length=50, blank=True, db_index=True)
    topics = models.JSONField(default=list, blank=True)
    stars_count = models.PositiveIntegerField(default=0, db_index=True)
    forks_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_visible = models.BooleanField(default=True, db_index=True)
    pushed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-stars_count", "-pushed_at", "name"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        indexes = [
            models.Index(fields=["is_visible", "is_featured"], name="proj_vis_feat_idx"),
            models.Index(fields=["-stars_count", "-pushed_at"], name="proj_stars_pushed_idx"),
        ]

    def __str__(self) -> str:
        return str(self.name)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            base_slug = slugify(self.name) or f"project-{self.pk or 'item'}"
            candidate_slug = base_slug
            counter = 1
            while Project.objects.filter(slug=candidate_slug).exclude(pk=self.pk).exists():
                candidate_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = candidate_slug
        super().save(*args, **kwargs)
