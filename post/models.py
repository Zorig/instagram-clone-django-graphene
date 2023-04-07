import hashlib

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    SearchVectorField,
)
from django.db import models

from utils.mixins import ActiveMixin, TimeStampMixin, UUIDMixin


def upload_to_user(instance, filename):
    ext = filename.split(".")[-1]
    string_to_hash = f"{instance.post.author.username}{instance.post.lng}{instance.post.lat}{instance.post.created_at}"
    hashed_filename = hashlib.md5(str(string_to_hash).encode("utf-8")).hexdigest()
    filename = f"{hashed_filename}.{ext}"
    return (
        f"uploads/{instance.post.author.id}/posts/{instance.post.created_at}/{filename}"
    )


class Post(ActiveMixin, TimeStampMixin, UUIDMixin):
    class PostQuerySet(models.QuerySet):
        def get_data(self):
            return self.select_related("author__profile").prefetch_related(
                "photos",
                models.Prefetch(
                    "post_comments",
                    queryset=Comment.objects.select_related("author__profile"),
                ),
            )

        def search(self, text):
            vector = SearchVector("caption")
            query = SearchQuery(text)
            return (
                self.annotate(rank=SearchRank(vector, query))
                .order_by("-rank")
                .filter(rank__gte=0.02)
            )

    caption = models.CharField(max_length=50)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lng = models.FloatField()
    lat = models.FloatField()

    vector_column = SearchVectorField(null=True, editable=False)

    objects = PostQuerySet.as_manager()

    class Meta:
        indexes = [GinIndex(fields=["vector_column"])]


class Photo(UUIDMixin):
    photo = models.ImageField(upload_to=upload_to_user)
    post = models.ForeignKey(
        Post, related_name="photos", on_delete=models.CASCADE, blank=True
    )


class Like(TimeStampMixin):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    liker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "liker"], name="unique_user_post_like"
            ),
        ]


class Comment(TimeStampMixin):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField()
