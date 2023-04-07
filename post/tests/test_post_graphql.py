import json
import uuid

import faker
import pytest

from account.tests.factory import UserFactory
from follow.tests.factory import FollowFactory

from .factory import PostFactory


@pytest.mark.django_db
def test_post_detail_query(client_query, django_assert_num_queries):
    user = UserFactory()
    post = PostFactory(author=user, lat=1, lng=1)

    with django_assert_num_queries(3):
        query = client_query(
            """
            query PostDetail($id: ID!){
                postDetail(id: $id) {
                    id
                    caption
                    author {
                        id
                        name
                    }
                    comments {
                        id
                    }
                }
            }
            """,
            variables={"id": str(post.id)},
        )
    content = json.loads(query.content)
    response = content["data"]["postDetail"]
    assert "errors" not in content
    assert response["id"] == str(post.id)
    assert response["author"] == {
        "id": str(user.id),
        "name": user.username,
    }
    assert response["caption"] == post.caption
    assert response["comments"] == []


@pytest.mark.django_db
def test_post_detail_query_invalid_id(client_query, django_assert_num_queries):
    with django_assert_num_queries(1):
        response = client_query(
            """
            query PostDetail($id: ID!){
                postDetail(id: $id) {
                    id
                    caption
                    author {
                        id
                        name
                    }
                    comments {
                        id
                    }
                }
            }
            """,
            variables={"id": str(uuid.uuid4())},
        )
    content = json.loads(response.content)
    assert content["data"]["postDetail"] is None


@pytest.mark.django_db
def test_post_mutation(client_query, client, user):
    client.force_login(user)

    f = faker.Faker()
    lat, lng = f.latlng()
    caption = f.word()

    mutation = client_query(
        """
        mutation Post($input: PostMutationInput!) {
          post(input: $input) {
            post {
              caption
              author {
                  id
                  name
              }
            }
            errors {
              messages
              field
            }
          }
        }
        """,
        variables={
            "input": {"caption": caption, "lat": float(lat), "lng": float(lng)},
        },
    )

    content = json.loads(mutation.content)
    assert content["data"]["post"]["errors"] == []
    assert content["data"]["post"]["post"] == {
        "caption": caption,
        "author": {"id": str(user.id), "name": user.username},
    }


@pytest.mark.skip()
@pytest.mark.django_db
def test_post_list_query(client_query, client, django_assert_num_queries, user):
    client.force_login(user)

    following = UserFactory()

    f = faker.Faker()

    posts = PostFactory.create_batch(3, caption=f.word(), author=following)
    FollowFactory(follower=user, followed=following)

    with django_assert_num_queries(4):
        query = client_query(
            """
            query Posts {
              postList {
                id
                caption
                photo
                author {
                  id
                  name
                }
                comments {
                  id
                  comment
                  author {
                    id
                    avatar
                    name
                  }
                  createdAt
                }
              }
            }
            """
        )

    content = json.loads(query.content)

    assert content["data"]["postList"] == [
        {
            "id": str(post.id),
            "caption": post.caption,
            "photo": f"http://testserver{post.photo.url}",
            "author": {"id": str(following.id), "name": following.username},
            "comments": [],
        }
        for post in posts
    ]
