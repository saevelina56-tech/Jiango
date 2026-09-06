# news/urls.py
from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.NewsListView.as_view(), name='list'),
    path('<int:pk>/', views.NewsDetailView.as_view(), name='detail'),
    path('create/', views.NewsCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.NewsUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.NewsDeleteView.as_view(), name='delete'),
]