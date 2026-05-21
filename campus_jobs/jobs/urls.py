from django.urls import path

from . import views

urlpatterns = [
    path("", views.job_list, name="home"),
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/apply/", views.apply_to_job, name="apply_to_job"),
    path("applications/", views.my_applications, name="my_applications"),
    path("resumes/", views.resume_list, name="resume_list"),
    path("resumes/new/", views.resume_create, name="resume_create"),
    path("dashboard/", views.employer_dashboard, name="employer_dashboard"),
]