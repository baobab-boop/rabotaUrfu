from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from rest_framework import generics, permissions

from .forms import ApplicationForm
from .models import Application, Job
from .serializers import ApplicationSerializer, JobSerializer


def job_list(request):
    q = request.GET.get("q", "").strip()
    job_type = request.GET.get("type", "").strip()

    jobs = Job.objects.select_related("employer").filter(is_active=True).order_by("-created_at")

    if q:
        jobs = jobs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q))
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    return render(request, "jobs/job_list.html", {"jobs": jobs, "q": q, "job_type": job_type})


def job_detail(request, pk: int):
    job = get_object_or_404(Job.objects.select_related("employer"), pk=pk, is_active=True)
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
                return redirect("my_applications") + f"?email={application.email}"
    else:
        form = ApplicationForm()

    return render(request, "jobs/application_form.html", {"form": form, "job": job})


def my_applications(request):
    email = request.GET.get("email", "").strip()
    applications = Application.objects.select_related("job", "job__employer").order_by("-created_at")

    if email:
        applications = applications.filter(email__iexact=email)

    return render(request, "jobs/my_applications.html", {"applications": applications, "email": email})


@staff_member_required
def employer_dashboard(request):
    jobs = (
        Job.objects.select_related("employer")
        .prefetch_related("applications")
        .annotate(app_count=Count("applications"))
        .order_by("-created_at")
    )
    return render(request, "jobs/dashboard.html", {"jobs": jobs})


class JobListAPIView(generics.ListCreateAPIView):
    queryset = Job.objects.select_related("employer").all().order_by("-created_at")
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]


class JobDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.select_related("employer").all()
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]


class ApplicationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Application.objects.select_related("job", "job__employer").all().order_by("-created_at")
        email = self.request.query_params.get("email")
        job_id = self.request.query_params.get("job")

        if email:
            queryset = queryset.filter(email__iexact=email)
        if job_id:
            queryset = queryset.filter(job_id=job_id)

        return queryset