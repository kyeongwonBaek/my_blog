from django.shortcuts import render
from .models import Post
from django.views.generic import ListView
# Create your views here.

class PostList(ListView):
    model = Post


# def index(request):
#     posts = Post.objects.all()
#     return render(
#         request,
#         'blog/index.html',
#         {
#         'posts' : posts,
#         },
#     )

