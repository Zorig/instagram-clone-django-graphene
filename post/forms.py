from django import forms

from .models import Comment, Photo, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("comment", "post")


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("caption", "lng", "lat")


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ("photo",)
