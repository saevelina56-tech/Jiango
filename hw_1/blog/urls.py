from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    # path('article_detail/<int:id>/', views.article_detail, name='article_detail')
    # path('post/<int:id>/', views.post_detail, name='post_detail'),
    path('articles/', views.article_list, name='article_list'),  
    path('articles/category/<slug:category_name>/', views.article_by_category, name='article_by_category'),  
    path('articles/search/', views.article_search, name='article_search'),
    path('articles/stats/', views.article_stats, name='article_stats'),
    path('books/', views.books, name='books'),
    path('create/', views.create_article, name='create_article'),
]