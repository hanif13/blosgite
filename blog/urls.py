from django.urls import path
from .views import *
urlpatterns = [
    path('',home , name='home'),
    path('blogs/',blogs,name='blogs'),
    path('category_blogs/<slug>',category_blogs,name='category_blogs'),
    path('tag_blogs/<slug>',tag_blogs,name='tag_blogs'),
    path('blog/<slug>',blog_details,name='blog_details'),
    path('add_replay/<str:blog_id>/<str:comment_id>',add_reply,name='add_replay'),
    path('like_blog/<int:pk>/', like_blog,name='like_blog'),
    path('search-blog',search_blog,name='search_blogs'),
    path('my-blogs',my_blogs,name='my_blogs'),
    path('add-blogs',add_blogs,name='add_blogs'),
    path('update_blogs/<str:slug>/',update_blogs,name='update_blogs'),
]
