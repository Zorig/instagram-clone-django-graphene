import pytest
from graphene_django.utils.testing import graphql_query
from graphene_file_upload.django.testing import file_graphql_query
from pytest_factoryboy import register

from account.tests.factory import ProfileFactory, UserFactory
from follow.tests.factory import FollowFactory
from post.tests.factory import CommentFactory, LikeFactory, PostFactory

@pytest.fixture()
def client_query(client):
    def func(*args, **kwargs):
        return graphql_query(*args, **kwargs, client=client)

    return func


# @pytest.fixture
# def client_query(client):
#     def func(*args, **kwargs):
#         return file_graphql_query(*args, **kwargs, client=client)
#
#     return func


register(CommentFactory)
register(FollowFactory)
register(LikeFactory)
register(ProfileFactory)
register(PostFactory)
register(UserFactory)
