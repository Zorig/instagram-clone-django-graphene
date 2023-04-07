import json

import faker
import pytest

from .factory import CommentFactory


@pytest.mark.django_db
def test_post_comments_query(client_query, post, user):
    comments_size = 3
    comments = CommentFactory.create_batch(comments_size, post=post)

    response = client_query(
        """
        query PostDetail($id: ID!){
            postDetail(id: $id) {
                id
                caption
                comments {
                    id
                    comment
                    author {
                        id
                        name
                    }
                }
            }
        }
        """,
        variables={"id": str(post.id)},
    )

    content = json.loads(response.content)
    response_comments = content["data"]["postDetail"]["comments"]

    assert len(response_comments) == comments_size
    assert response_comments == [
        {
            "id": str(comment.id),
            "comment": comment.comment,
            "author": {"id": str(comment.author.id), "name": comment.author.username},
        }
        for comment in comments
    ]


@pytest.mark.django_db
def test_post_comment_mutation(client_query, client, post, user):
    client.force_login(user)
    f = faker.Faker()
    comment = f.paragraph()
    mutation = client_query(
        """
        mutation Comment($input: CommentMutationInput!) {
          comment(input: $input) {
            comment {
              comment
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
        variables={"input": {"comment": comment, "post": str(post.id)}},
    )

    content = json.loads(mutation.content)
    response = content['data']['comment']
    assert response["comment"] == {
        "comment": comment,
        "author": {"id": str(user.id), "name": user.username},
    }
    assert response['errors'] == []
