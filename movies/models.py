from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')

    def __str__(self):
        return str(self.id) + ' - ' + self.name

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_hidden = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name


class ReviewReport(models.Model):
    class Reason(models.TextChoices):
        SPAM = 'spam', 'Spam or irrelevant content'
        OFFENSIVE = 'offensive', 'Offensive or abusive content'
        OTHER = 'other', 'Other inappropriate content'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending review'
        UPHELD = 'upheld', 'Report upheld'
        DISMISSED = 'dismissed', 'Report dismissed'

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    reason = models.CharField(max_length=20, choices=Reason.choices)
    details = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['review', 'reporter'], name='one_report_per_user_review')]

    def __str__(self):
        return f'Report #{self.pk} for review #{self.review_id}'
