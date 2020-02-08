from django.urls import path
from . import views


urlpatterns = [
    path('search/<str:q>/', views.PostSearch.as_view()),
    path('category/<str:slug>/', views.PostListByCategory.as_view()),
    path('tag/<str:slug>/', views.PostListByTag.as_view()),
    path('<int:pk>/update/', views.PostUpdate.as_view()),
    path('<int:pk>/new_comment/', views.new_comment),
    path('delete_comment/<int:pk>/', views.delete_comment),
    path('edit_comment/<int:pk>/', views.CommentUpdate.as_view()),
    path('delete_post/<int:pk>/', views.delete_post),
    path('<int:pk>/', views.PostDetail.as_view()),
    path('create/', views.PostCreate.as_view()),
    path('', views.PostList.as_view()),

]