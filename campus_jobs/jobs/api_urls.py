from django.urls import path
from rest_framework.routers import DefaultRouter

from .api_views import (
    ApplicationViewSet,
    DashboardStatsAPIView,
    DepartmentViewSet,
    EmployerViewSet,
    FacultyViewSet,
    InterviewViewSet,
    JobCategoryViewSet,
    JobSkillViewSet,
    JobViewSet,
    ResumeViewSet,
    SkillViewSet,
)

router = DefaultRouter()
router.register(r"faculties", FacultyViewSet, basename="faculty")
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"employers", EmployerViewSet, basename="employer")
router.register(r"categories", JobCategoryViewSet, basename="category")
router.register(r"skills", SkillViewSet, basename="skill")
router.register(r"resumes", ResumeViewSet, basename="resume")
router.register(r"jobs", JobViewSet, basename="job")
router.register(r"job-skills", JobSkillViewSet, basename="job-skill")
router.register(r"applications", ApplicationViewSet, basename="application")
router.register(r"interviews", InterviewViewSet, basename="interview")

urlpatterns = [
    path("stats/", DashboardStatsAPIView.as_view(), name="dashboard-stats"),
]

urlpatterns += router.urls