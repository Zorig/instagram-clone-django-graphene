import graphene
from graphene_django import DjangoObjectType

from .models import Profile


class ProfileType(DjangoObjectType):
    name = graphene.String()
    id = graphene.ID()

    class Meta:
        model = Profile
        fields = ("id", "avatar", "bio", "name", "website")

    def resolve_avatar(root, info):
        return info.context.build_absolute_uri(root.avatar.url) if root.avatar else ""

    def resolve_name(root, info):
        return root.user.username

    def resolve_id(root, info):
        return root.user.id
