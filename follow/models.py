from django.conf import settings
from django.db import models

from utils.mixins import TimeStampMixin, UUIDMixin


class Follow(TimeStampMixin, UUIDMixin):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
    )

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"
