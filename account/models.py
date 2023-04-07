from django.contrib.auth.models import User
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def upload_to_user(instance, filename):
    return f"uploads/{instance.user.id}/avatar/{filename}"


class Profile(models.Model):
    class ProfileManager(models.QuerySet):
        def search(self, text):
            vector = SearchVector("user__username")
            query = SearchQuery(text)
            return (
                self.annotate(rank=SearchRank(vector, query))
                .order_by("-rank")
                .filter(rank__gte=0.02)
            )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.CharField(max_length=250)
    website = models.URLField()
    avatar = models.ImageField(upload_to=upload_to_user)

    objects = ProfileManager.as_manager()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
