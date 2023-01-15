"""kalamakara URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from frontend.views import home, team, contact, submit_contact, my_submission, my_submissions, upload, api_insert_update_submission, api_latest_submission, api_get_submission, submit_xray, submit_ctscan
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('home/', home),
    path('team/', team),
    path('contact/', contact),
    path('submit_contact/', submit_contact),
    path('submit_xray/', submit_xray),
    path('submit_ctscan/', submit_ctscan),
    path('my_submission/', my_submission),
    path('my_submissions/', my_submissions),
    path('upload/', upload),
    path('api_insert_update_submission/', api_insert_update_submission),
    path('api_get_submission/', api_get_submission),
    path('api_latest_submission/', api_latest_submission),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.THUMBNAIL_URL, document_root=settings.THUMBNAIL_ROOT)
