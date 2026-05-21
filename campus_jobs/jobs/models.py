from django.db import models


class Faculty(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=120)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["faculty", "name"], name="uniq_department_per_faculty")
        ]

    def __str__(self):
        return f"{self.name} ({self.faculty.code})"


class Employer(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employers",
    )
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class JobCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Resume(models.Model):
    student_full_name = models.CharField(max_length=120)
    student_email = models.EmailField()
    phone = models.CharField(max_length=20)
    title = models.CharField(max_length=120)
    summary = models.TextField()
    file_name = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_full_name} — {self.title}"


class Job(models.Model):
    class JobType(models.TextChoices):
        ASSISTANT = "assistant", "Ассистент преподавателя"
        ADMINISTRATIVE = "administrative", "Административная работа"
        RESEARCH = "research", "Исследовательский проект"
        INTERNSHIP = "internship", "Стажировка"

    title = models.CharField(max_length=120)
    description = models.TextField()
    location = models.CharField(max_length=120)
    job_type = models.CharField(max_length=20, choices=JobType.choices)

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="jobs")
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )

    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)

    skills = models.ManyToManyField(Skill, through="JobSkill", related_name="jobs", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class JobSkill(models.Model):
    class RequiredLevel(models.TextChoices):
        BASIC = "basic", "Базовый"
        INTERMEDIATE = "intermediate", "Средний"
        ADVANCED = "advanced", "Продвинутый"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="job_skills")
    required_level = models.CharField(max_length=20, choices=RequiredLevel.choices, default=RequiredLevel.BASIC)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["job", "skill"], name="uniq_job_skill")
        ]

    def __str__(self):
        return f"{self.job.title} — {self.skill.name}"


class Application(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        REVIEW = "review", "На рассмотрении"
        INTERVIEW = "interview", "Интервью"
        OFFER = "offer", "Предложение"
        REJECTED = "rejected", "Отклонена"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications")

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    cover_letter = models.TextField()

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["job", "email"], name="uniq_application_job_email")
        ]

    def __str__(self):
        return f"{self.full_name} — {self.job.title}"


class Interview(models.Model):
    class InterviewStatus(models.TextChoices):
        PLANNED = "planned", "Запланировано"
        DONE = "done", "Проведено"
        CANCELED = "canceled", "Отменено"

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="interviews")
    scheduled_at = models.DateTimeField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=InterviewStatus.choices, default=InterviewStatus.PLANNED)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.application.full_name} — {self.scheduled_at}"