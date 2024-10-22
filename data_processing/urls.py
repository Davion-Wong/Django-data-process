from django.urls import path
from . import views

urlpatterns = [
    path('api/upload/', views.api_upload_file, name='api_upload_file'),
]