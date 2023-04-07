from django.contrib import admin

from .models import Comment, Like, Post, Photo


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "created_at")
    search_fields = ("created_at", "author")
    list_filter = ("author",)


admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Photo)
