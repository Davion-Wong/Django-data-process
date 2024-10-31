from django.urls import path
from . import views

urlpatterns = [
    path('api/csrf/', views.csrf_token_view, name='csrf_token'),
    path('api/upload/', views.api_upload_file, name='api_upload_file'),
    path('display/', views.dataset_display_view, name='dataset_display'),
    path('data/display/', views.dataset_display_view, name='dataset_display_view'),
    path('api/dataset/', views.get_processed_dataset, name='get_processed_dataset'),
    path('api/task-status/<str:task_id>/', views.check_task_status, name='check_task_status'),
    path('get-processed-dataset/', views.get_processed_dataset, name='get_processed_dataset'),
    path('api/processed_data_status/', views.get_processed_data_status, name='processed_data_status'),
]