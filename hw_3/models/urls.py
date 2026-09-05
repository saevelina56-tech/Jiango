from django.urls import path
from .view import AnalyticsView

urlpatterns = [
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
]