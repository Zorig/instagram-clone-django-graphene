import graphene
from django.http import Http404
from graphene_django import DjangoListField, DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_file_upload.scalars import Upload

from account.models import User
from account.schema import ProfileType

from .forms import CommentForm, PhotoForm, PostForm
from .models import Comment, Like, Photo, Post


class CommentType(DjangoObjectType):
    author = graphene.Field(ProfileType)

    class Meta:
        model = Comment
        fields = ("author", "created_at", "comment", "id")

    def resolve_author(root, info):
        return root.author.profile


class CommentMutation(DjangoModelFormMutation):
    comment = graphene.Field(CommentType)

    class Meta:
        form_class = CommentForm

    @classmethod
    def perform_mutate(cls, form, info):
        obj = form.save(commit=False)
        obj.author = info.context.user
        obj.save()
        kwargs = {cls._meta.return_field_name: obj}
        return cls(errors=[], **kwargs)


class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = ("id", "liker", "post")


class LikeMutation(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)

    like = graphene.Field(LikeType)

    @classmethod
    def mutate(cls, root, info, post_id):
        like = Like.objects.create(post_id=post_id, liker=info.context.user)
        return LikeMutation(like=like)


class PhotoType(DjangoObjectType):
    photo = graphene.String()

    class Meta:
        model = Photo
        fields = ("photo",)

    def resolve_photo(root, info):
        return info.context.build_absolute_uri(root.photo.url)


class PostType(DjangoObjectType):
    author = graphene.Field(ProfileType)
    comments = DjangoListField(CommentType)
    liked = graphene.Boolean()
    photos = DjangoListField(PhotoType)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "caption",
            "comments",
            "created_at",
            "photos",
            "liked",
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.prefetch_related("photos")

    def resolve_author(root, info):
        return root.author.profile

    def resolve_comments(root, info):
        return root.post_comments.all()

    def resolve_liked(root, info):
        return root.likes.filter(liker=info.context.user).exists()

    def resolve_photos(root, info):
        return root.photos.all()


class PostMutation(DjangoModelFormMutation):
    post = graphene.Field(PostType)

    class Meta:
        form_class = PostForm

    @classmethod
    def perform_mutate(cls, form, info):
        obj = form.save(commit=False)
        obj.author = info.context.user
        obj.save()
        kwargs = {cls._meta.return_field_name: obj}
        return cls(errors=[], **kwargs)


class PhotoMutation(DjangoModelFormMutation):
    photo = graphene.Field(PhotoType)

    class Meta:
        form_class = PhotoForm


class ProfilePosts(DjangoObjectType):
    posts = DjangoListField(PostType)
    profile = graphene.Field(ProfileType)

    class Meta:
        model = User
        fields = ("id", "username", "email", "profile", "posts")

    def resolve_profile(root, info):
        return root.profile

    def resolve_posts(root, info):
        return root.post_set.all()


class SearchResult(graphene.Union):
    class Meta:
        types = (PostType, ProfileType)


class SearchTypeEnum(graphene.Enum):
    post = PostType
    people = ProfileType


class Query(graphene.ObjectType):
    post_detail = graphene.Field(PostType, id=graphene.ID(required=True))
    post_list = DjangoListField(PostType)
    profile = graphene.Field(ProfilePosts, id=graphene.ID(required=True))
    likes = graphene.List(graphene.ID)
    search = graphene.List(
        SearchResult,
        query=graphene.String(required=True),
        type=graphene.String(),
    )

    def resolve_post_list(root, info):
        return Post.objects.get_data().filter(
            author__in=info.context.user.following.all().values_list("followed")
        )

    def resolve_post_detail(root, info, id):
        try:
            return Post.objects.get_data().get(id=id)
        except Post.DoesNotExist:
            return None

    def resolve_profile(root, info, id):
        try:
            return User.objects.select_related("profile").get(id=id)
        except User.DoesNotExist:
            return None

    def resolve_likes(root, info):
        return (
            Like.objects.filter(liker=info.context.user)
            .order_by("-created_at")
            .values_list("post_id", flat=True)
        )

    def resolve_search(root, info, query, type="posts"):
        if type == "people":
            res = User.objects.search(query).select_related("profile")
            print(res)
        return Post.objects.search(query)


class UploadMutation(graphene.Mutation):
    class Arguments:
        photo = Upload(required=True, description="Photo file")
        post_id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, photo, post_id):
        form = PhotoForm(files={"photo": photo})
        if form.is_valid():
            photo_file = form.save(commit=False)
            photo_file.post_id = post_id
            photo_file.save()
            return cls(success=True)
        else:
            errors = form.errors
            return cls(success=False, errors=errors)


class Mutation(graphene.ObjectType):
    like = LikeMutation.Field()
    post = PostMutation.Field()
    comment = CommentMutation.Field()
    upload = UploadMutation.Field()
