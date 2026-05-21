from django.utils import timezone
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_serializers import (
    ApplicationSerializer,
    ApplicationStatusSerializer,
    DepartmentSerializer,
    EmployerSerializer,
    FacultySerializer,
    InterviewSerializer,
    JobCategorySerializer,
    JobSerializer,
    JobSkillSerializer,
    ResumeSerializer,
    SkillSerializer,
)
from .models import (
    Application,
    Department,
    Employer,
    Faculty,
    Interview,
    Job,
    JobCategory,
    JobSkill,
    Resume,
    Skill,
)


class StaffWriteReadPublicViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class PublicCreateStaffOnlyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class StaffOnlyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_permissions(self):
        return [permissions.IsAdminUser()]


class FacultyViewSet(StaffWriteReadPublicViewSet):
    queryset = Faculty.objects.all().order_by("name")
    serializer_class = FacultySerializer
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]


class DepartmentViewSet(StaffWriteReadPublicViewSet):
    queryset = Department.objects.select_related("faculty").all().order_by("name")
    serializer_class = DepartmentSerializer
    search_fields = ["name", "faculty__name", "faculty__code"]
    ordering_fields = ["name"]


class EmployerViewSet(StaffWriteReadPublicViewSet):
    queryset = Employer.objects.select_related("department", "department__faculty").all().order_by("name")
    serializer_class = EmployerSerializer
    search_fields = ["name", "contact_email", "description"]
    ordering_fields = ["name", "contact_email"]


class JobCategoryViewSet(StaffWriteReadPublicViewSet):
    queryset = JobCategory.objects.all().order_by("name")
    serializer_class = JobCategorySerializer
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "slug"]


class SkillViewSet(StaffWriteReadPublicViewSet):
    queryset = Skill.objects.all().order_by("name")
    serializer_class = SkillSerializer
    search_fields = ["name"]
    ordering_fields = ["name"]


class ResumeViewSet(PublicCreateStaffOnlyViewSet):
    queryset = Resume.objects.all().order_by("-created_at")
    serializer_class = ResumeSerializer
    search_fields = ["student_full_name", "student_email", "title"]
    ordering_fields = ["created_at", "student_full_name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        email = self.request.query_params.get("email")
        if email:
            queryset = queryset.filter(student_email__iexact=email)
        return queryset


class JobViewSet(StaffWriteReadPublicViewSet):
    queryset = Job.objects.select_related("employer", "department", "category").prefetch_related("job_skills__skill").all().order_by("-created_at")
    serializer_class = JobSerializer
    search_fields = ["title", "description", "location", "employer__name", "category__name"]
    ordering_fields = ["created_at", "deadline", "title"]

    def get_queryset(self):
        queryset = super().get_queryset()
        job_type = self.request.query_params.get("type")
        category = self.request.query_params.get("category")
        active = self.request.query_params.get("active")

        if job_type:
            queryset = queryset.filter(job_type=job_type)
        if category:
            queryset = queryset.filter(category_id=category)
        if active in {"0", "1"}:
            queryset = queryset.filter(is_active=active == "1")

        return queryset


class JobSkillViewSet(StaffWriteReadPublicViewSet):
    queryset = JobSkill.objects.select_related("job", "skill").all()
    serializer_class = JobSkillSerializer
    search_fields = ["job__title", "skill__name", "required_level"]
    ordering_fields = ["required_level"]


class ApplicationViewSet(PublicCreateStaffOnlyViewSet):
    queryset = Application.objects.select_related("job", "job__employer", "resume").all().order_by("-created_at")
    serializer_class = ApplicationSerializer
    search_fields = ["full_name", "email", "phone", "job__title", "status"]
    ordering_fields = ["created_at", "updated_at", "status"]

    def get_queryset(self):
        queryset = super().get_queryset()
        email = self.request.query_params.get("email")
        job_id = self.request.query_params.get("job")
        status_param = self.request.query_params.get("status")

        if email:
            queryset = queryset.filter(email__iexact=email)
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def set_status(self, request, pk=None):
        application = self.get_object()
        serializer = ApplicationStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application.status = serializer.validated_data["status"]
        application.save(update_fields=["status", "updated_at"])

        return Response(ApplicationSerializer(application, context={"request": request}).data, status=status.HTTP_200_OK)


class InterviewViewSet(StaffOnlyViewSet):
    queryset = Interview.objects.select_related("application", "application__job").all().order_by("-scheduled_at")
    serializer_class = InterviewSerializer
    search_fields = ["application__full_name", "application__job__title", "location", "status"]
    ordering_fields = ["scheduled_at", "status"]


class DashboardStatsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        data = {
            "faculties": Faculty.objects.count(),
            "departments": Department.objects.count(),
            "employers": Employer.objects.count(),
            "categories": JobCategory.objects.count(),
            "skills": Skill.objects.count(),
            "resumes": Resume.objects.count(),
            "jobs": Job.objects.count(),
            "active_jobs": Job.objects.filter(is_active=True).count(),
            "applications": Application.objects.count(),
            "pending_applications": Application.objects.filter(status=Application.Status.NEW).count(),
            "interviews": Interview.objects.count(),
            "interviews_today": Interview.objects.filter(scheduled_at__date=timezone.localdate()).count(),
        }
        return Response(data)