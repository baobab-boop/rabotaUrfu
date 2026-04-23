from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"faculties", views.FacultyViewSet, basename="faculty")
router.register(r"departments", views.DepartmentViewSet, basename="department")
router.register(r"employers", views.EmployerViewSet, basename="employer")
router.register(r"categories", views.JobCategoryViewSet, basename="category")
router.register(r"skills", views.SkillViewSet, basename="skill")
router.register(r"resumes", views.ResumeViewSet, basename="resume")
router.register(r"jobs", views.JobViewSet, basename="job")
router.register(r"job-skills", views.JobSkillViewSet, basename="job-skill")
router.register(r"applications", views.ApplicationViewSet, basename="application")
router.register(r"interviews", views.InterviewViewSet, basename="interview")

urlpatterns = [
    path("", views.job_list, name="home"),
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/apply/", views.apply_to_job, name="apply_to_job"),
    path("applications/", views.my_applications, name="my_applications"),
    path("resumes/", views.resume_list, name="resume_list"),
    path("resumes/new/", views.resume_create, name="resume_create"),
    path("dashboard/", views.employer_dashboard, name="employer_dashboard"),
    path("api/", include(router.urls)),
]