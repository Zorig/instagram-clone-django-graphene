import graphene
from graphene_django.debug import DjangoDebug

from post.schema import Mutation as PostMutation
from post.schema import Query as PostQuery


class Query(PostQuery, graphene.ObjectType):

    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutation(PostMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
