from django.db import models


class ContactMessage(models.Model):
    objects = models.Manager()

    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self) -> str:
        return f"{self.name} - {self.subject or 'No Subject'} ({self.created_at:%Y-%m-%d %H:%M})"
