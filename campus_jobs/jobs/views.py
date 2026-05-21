from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework import permissions, viewsets
from django.contrib import messages

from .forms import ApplicationForm, ResumeForm
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
from .serializers import (
    ApplicationSerializer,
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


def job_list(request):
    q = request.GET.get("q", "").strip()
    job_type = request.GET.get("type", "").strip()
    category = request.GET.get("category", "").strip()

    jobs = (
        Job.objects.select_related("employer", "department", "category")
        .prefetch_related("job_skills__skill")
        .filter(is_active=True)
        .order_by("-created_at")
    )

    if q:
        jobs = jobs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q))
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if category:
        jobs = jobs.filter(category_id=category)

    categories = JobCategory.objects.all().order_by("name")
    return render(
        request,
        "jobs/job_list.html",
        {"jobs": jobs, "q": q, "job_type": job_type, "category": category, "categories": categories},
    )


def job_detail(request, pk: int):
    job = get_object_or_404(
        Job.objects.select_related("employer", "department", "category").prefetch_related("job_skills__skill"),
        pk=pk,
        is_active=True,
    )
    return render(request, "jobs/job_detail.html", {"job": job})


def apply_to_job(request, pk: int):
    job = get_object_or_404(Job, pk=pk, is_active=True)

    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            if Application.objects.filter(job=job, email__iexact=email).exists():
                form.add_error("email", "Вы уже отправляли заявку на эту вакансию.")
            else:
                application = form.save(commit=False)
                application.job = job
                application.save()
                return redirect(f"{reverse('my_applications')}?email={application.email}")
    else:
        form = ApplicationForm()

    return render(request, "jobs/application_form.html", {"form": form, "job": job})


def my_applications(request):
    email = request.GET.get("email", "").strip()
    applications = (
        Application.objects.select_related("job", "job__employer", "resume")
        .order_by("-created_at")
    )

    if email:
        applications = applications.filter(email__iexact=email)

    return render(request, "jobs/my_applications.html", {"applications": applications, "email": email})


def resume_list(request):
    email = request.GET.get("email", "").strip()
    resumes = Resume.objects.all().order_by("-created_at")

    if email:
        resumes = resumes.filter(student_email__iexact=email)

    return render(request, "jobs/resume_list.html", {"resumes": resumes, "email": email})


def resume_create(request):
    if request.method == "POST":
        form = ResumeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("resume_list")
    else:
        form = ResumeForm()

    return render(request, "jobs/resume_form.html", {"form": form})


@staff_member_required
def employer_dashboard(request):
    if request.method == "POST":
        application_id = request.POST.get("application_id")
        new_status = request.POST.get("status")

        allowed_statuses = dict(Application.Status.choices)

        if application_id and new_status in allowed_statuses:
            application = get_object_or_404(Application, pk=application_id)
            application.status = new_status
            application.save(update_fields=["status", "updated_at"])
            messages.success(request, f"Статус заявки '{application.full_name}' обновлён.")
        else:
            messages.error(request, "Не удалось обновить статус заявки.")

        return redirect("employer_dashboard")

    jobs = (
        Job.objects.select_related("employer", "department", "category")
        .annotate(app_count=Count("applications"))
        .order_by("-created_at")
    )

    applications = (
        Application.objects.select_related("job", "job__employer", "resume")
        .order_by("-created_at")
    )

    totals = {
        "jobs": Job.objects.count(),
        "applications": Application.objects.count(),
        "resumes": Resume.objects.count(),
        "interviews": Interview.objects.count(),
    }

    return render(
        request,
        "jobs/dashboard.html",
        {
            "jobs": jobs,
            "applications": applications,
            "totals": totals,
            "status_choices": Application.Status.choices,
        },
    )

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all().order_by("name")
    serializer_class = FacultySerializer
    permission_classes = [permissions.AllowAny]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related("faculty").all().order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.AllowAny]


class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.select_related("department", "department__faculty").all().order_by("name")
    serializer_class = EmployerSerializer
    permission_classes = [permissions.AllowAny]


class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all().order_by("name")
    serializer_class = JobCategorySerializer
    permission_classes = [permissions.AllowAny]


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all().order_by("name")
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]


class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all().order_by("-created_at")
    serializer_class = ResumeSerializer
    permission_classes = [permissions.AllowAny]


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related("employer", "department", "category").prefetch_related("job_skills__skill").all().order_by("-created_at")
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]


class JobSkillViewSet(viewsets.ModelViewSet):
    queryset = JobSkill.objects.select_related("job", "skill").all()
    serializer_class = JobSkillSerializer
    permission_classes = [permissions.AllowAny]


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related("job", "job__employer", "resume").all().order_by("-created_at")
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        email = self.request.query_params.get("email")
        job_id = self.request.query_params.get("job")
        status = self.request.query_params.get("status")

        if email:
            queryset = queryset.filter(email__iexact=email)
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.select_related("application", "application__job").all().order_by("-scheduled_at")
    serializer_class = InterviewSerializer
    permission_classes = [permissions.AllowAny]