from django.urls import path
from . import views

urlpatterns = [
    path('api/upload/', views.api_upload_file, name='api_upload_file'),
    path('api/dataset/', views.get_processed_dataset, name='get_processed_dataset'),
    path('display/', views.dataset_display_view, name='dataset_display'),
    path('api/task-status/<str:task_id>/', views.check_task_status, name='check_task_status'),
    path('api/start-task/', views.start_long_task, name='start_long_task'),
    path('api/task-status/<str:task_id>/', views.check_task_status, name='check_task_status'),
    path('api/task-progress/<str:task_id>/', views.check_task_progress, name='check_task_progress'),
    path('api/csrf/', views.csrf_token_view, name='csrf_token'),
    path('data/display/', views.dataset_display_view, name='dataset_display_view'),
    path('get-processed-dataset/', views.get_processed_dataset, name='get_processed_dataset'),
    path('api/processed_data_status/', views.get_processed_data_status, name='processed_data_status'),
]