from django.urls import path

from . import views

urlpatterns = [
    path("", views.job_list, name="home"),
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/apply/", views.apply_to_job, name="apply_to_job"),
    path("applications/", views.my_applications, name="my_applications"),
    path("dashboard/", views.employer_dashboard, name="employer_dashboard"),
    path("api/jobs/", views.JobListAPIView.as_view(), name="api_jobs"),
    path("api/jobs/<int:pk>/", views.JobDetailAPIView.as_view(), name="api_job_detail"),
    path("api/applications/", views.ApplicationListCreateAPIView.as_view(), name="api_applications"),
]