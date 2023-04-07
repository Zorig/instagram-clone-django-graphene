import factory
from django.contrib.auth.models import User

from ..models import Profile


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    username = factory.Faker("user_name")


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    website = factory.Faker("domain_name")
    bio = factory.Faker("word")
    user = factory.SubFactory(UserFactory)
