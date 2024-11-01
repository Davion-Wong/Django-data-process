"""
URL configuration for data_inference project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from data_processing import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('data/', include('data_processing.urls')),
    path( '', lambda request: HttpResponseRedirect( 'http://localhost:3000' ) ),
    path('data/api/upload/', views.api_upload_file, name='api_upload_file'),
]
