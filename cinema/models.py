from django.db import models


class Cinema(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.city})"


class Theatre(models.Model):
    SCREEN_STANDARD = "standard"
    SCREEN_IMAX = "imax"
    SCREEN_DOLBY = "dolby"
    SCREEN_3D = "3d"

    SCREEN_TYPE_CHOICES = [
        (SCREEN_STANDARD, "Standard"),
        (SCREEN_IMAX, "IMAX"),
        (SCREEN_DOLBY, "Dolby"),
        (SCREEN_3D, "3D"),
    ]

    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name="theatres")
    name = models.CharField(max_length=120)
    capacity = models.PositiveIntegerField()
    screen_type = models.CharField(max_length=30, choices=SCREEN_TYPE_CHOICES, default=SCREEN_STANDARD)

    class Meta:
        unique_together = ("cinema", "name")
        ordering = ["cinema__name", "name"]

    def __str__(self):
        return f"{self.cinema.name} - {self.name}"
