import factory

from ..models import Follow


class FollowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Follow
