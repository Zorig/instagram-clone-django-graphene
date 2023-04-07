import factory
from django.core.files.uploadedfile import SimpleUploadedFile

from account.tests.factory import UserFactory

from ..models import Comment, Like, Photo, Post


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    class Params:
        geo_data = factory.Faker("location_on_land")
        name = factory.Faker("name")

    caption = factory.Faker("word")
    author = factory.SubFactory(UserFactory)
    lat = factory.LazyAttribute(lambda x: x.geo_data[0])
    lng = factory.LazyAttribute(lambda x: x.geo_data[1])


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    comment = factory.Faker("paragraph")


class LikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Like

    post = factory.SubFactory(PostFactory)
    liker = factory.SubFactory(UserFactory)


class PhotoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Photo

    photo = SimpleUploadedFile(
        name="a.jpeg",
        content=b"",
        content_type="image/jpeg",
    )
    post = factory.SubFactory(PostFactory)
