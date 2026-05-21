from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("jobs.urls")),
    path("api/", include("jobs.api_urls")),
]