from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration_mins = models.PositiveIntegerField()
    genre = models.CharField(max_length=120)
    rating = models.CharField(max_length=20)
    poster_url = models.URLField(blank=True)
    release_date = models.DateField()
    is_featured = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["-release_date", "title"]

    def __str__(self):
        return self.title


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="sessions")
    theatre = models.ForeignKey("cinema.Theatre", on_delete=models.CASCADE, related_name="sessions")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    seats_available = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.movie.title} @ {self.start_time:%Y-%m-%d %H:%M}"
