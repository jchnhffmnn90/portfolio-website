from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "language",
        "stars_count",
        "forks_count",
        "is_featured",
        "is_visible",
        "pushed_at",
    )
    list_filter = ("is_featured", "is_visible", "language")
    search_fields = ("name", "description", "language")
    prepopulated_fields = {"slug": ("name",)}
