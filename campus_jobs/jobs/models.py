from django.db import models


class Employer(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    ASSISTANT = "assistant"
    ADMINISTRATIVE = "administrative"
    RESEARCH = "research"
    INTERNSHIP = "internship"

    JOB_TYPES = [
        (ASSISTANT, "Ассистент преподавателя"),
        (ADMINISTRATIVE, "Административная работа"),
        (RESEARCH, "Исследовательский проект"),
        (INTERNSHIP, "Стажировка"),
    ]

    title = models.CharField(max_length=120)
    description = models.TextField()
    location = models.CharField(max_length=120)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="jobs")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    PENDING = "pending"
    INTERVIEW = "interview"
    APPROVED = "approved"
    REJECTED = "rejected"

    STATUS_CHOICES = [
        (PENDING, "На рассмотрении"),
        (INTERVIEW, "Приглашение на интервью"),
        (APPROVED, "Одобрено"),
        (REJECTED, "Отклонено"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} — {self.job.title}"