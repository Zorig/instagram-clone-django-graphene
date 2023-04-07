import json

import pytest

from post.tests.factory import PostFactory

from .factory import LikeFactory


@pytest.mark.django_db
def test_likes_query(client_query, client, django_assert_num_queries, user):
    client.force_login(user)
    posts = PostFactory.create_batch(10)
    [LikeFactory(post=post, liker=user) for post in posts]
    with django_assert_num_queries(3):
        query = client_query(
            """
            query Likes {
              likes
            }
            """
        )
    content = json.loads(query.content)
    response = content["data"]["likes"]
    assert len(response) == len(posts)


@pytest.mark.django_db
def test_post_like_query(client_query, client, post, user):
    client.force_login(user)
    LikeFactory(liker=user, post=post)
    query = client_query(
        """
        query PostDetail($id: ID!) {
          postDetail(id: $id) {
            id
            caption
            liked
          }
        }
        """,
        variables={"id": str(post.id)},
    )
    content = json.loads(query.content)
    response = content["data"]["postDetail"]
    assert response["liked"]


@pytest.mark.django_db
def test_like_mutation(client_query, client, user):
    client.force_login(user)
    post = PostFactory(author=user, lat=1, lng=1)
    mutation = client_query(
        """
        mutation Like($id: ID!) {
            like(postId: $id) {
                like {
                  id
                  post {
                    id
                  }
                  liker {
                    id
                  }
                }
            }
        }
        """,
        variables={"id": str(post.id)},
    )
    content = json.loads(mutation.content)
    response = content["data"]["like"]["like"]
    assert "errors" not in content
    assert response["post"] == {"id": str(post.id)}
    assert response["liker"] == {"id": str(user.id)}


@pytest.mark.django_db
def test_like_mutation_duplicate(client_query, client, post, user):
    client.force_login(user)
    post = PostFactory(author=user, lat=1, lng=1)
    LikeFactory(liker=user, post=post)

    mutation = client_query(
        """
        mutation Like($id: ID!) {
            like(postId: $id) {
                like {
                  id
                  post {
                    id
                  }
                  liker {
                    id
                  }
                }
            }
        }
        """,
        variables={"id": str(post.id)},
    )
    content = json.loads(mutation.content)
    assert "errors" not in content
    assert content["data"] == {"like": {"like": None}}
