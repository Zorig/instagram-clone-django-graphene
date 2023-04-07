import json
import uuid

import faker
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from post.tests.factory import PostFactory


@pytest.mark.django_db
def test_user_profile_query(client_query, user):
    f = faker.Faker()
    title = f.word()
    user.profile.avatar = SimpleUploadedFile(
        f"{title}.jpg", content=f.image(), content_type="image/jpg"
    )
    user.profile.save(update_fields=["avatar"])
    query = client_query(
        """
        query Profile($id: ID!) {
            profile(id: $id) {
                profile {
                    avatar
                    name
                    bio
                    website
                }
            }
        }
        """,
        variables={"id": str(user.pk)},
    )
    content = json.loads(query.content)
    assert content["data"]["profile"]["profile"]["name"] == user.username


@pytest.mark.django_db
def test_user_posts_query(client_query, user):
    post_size = 10
    user_posts = PostFactory.create_batch(post_size, author=user)

    query = client_query(
        """
        query Profile($id: ID!) {
            profile(id: $id) {
                posts {
                    id
                    caption
                    author {
                        id
                    }
                }
            }
        }
        """,
        variables={"id": str(user.pk)},
    )
    content = json.loads(query.content)
    response_posts = content["data"]["profile"]["posts"]
    assert len(response_posts) is post_size
    assert response_posts == [
        {"id": str(post.id), "caption": post.caption, "author": {"id": str(user.id)}}
        for post in user_posts
    ]


@pytest.mark.django_db
def test_invalid_user_profile_query(client_query):
    invalid_user_id = uuid.uuid4()

    query = client_query(
        """
        query Profile($id: ID!) {
            profile(id: $id) {
                profile {
                    avatar
                    name
                    bio
                    website
                }
            }
        }
        """,
        variables={"id": str(invalid_user_id)},
    )
    content = json.loads(query.content)
    assert content["data"]["profile"] is None
