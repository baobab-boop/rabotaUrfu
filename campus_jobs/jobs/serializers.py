from django.utils import timezone
from rest_framework import serializers

from .models import Employer, Job, Application


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ["id", "name", "contact_email", "description", "website"]

    name = serializers.CharField(
        min_length=2,
        max_length=255,
        error_messages={
            "required": "Укажи название работодателя.",
            "blank": "Название работодателя не может быть пустым.",
            "min_length": "Название работодателя должно быть не короче 2 символов.",
            "max_length": "Название работодателя должно быть не длиннее 255 символов.",
        },
    )
    contact_email = serializers.EmailField(
        error_messages={
            "required": "Укажи контактный email.",
            "invalid": "Введите корректный email.",
        }
    )


class JobSerializer(serializers.ModelSerializer):
    employer = serializers.PrimaryKeyRelatedField(queryset=Employer.objects.all())
    title = serializers.CharField(
        min_length=5,
        max_length=120,
        error_messages={
            "required": "Укажи название вакансии.",
            "blank": "Название вакансии не может быть пустым.",
            "min_length": "Название должно быть не короче 5 символов.",
            "max_length": "Название должно быть не длиннее 120 символов.",
        },
    )
    description = serializers.CharField(
        min_length=20,
        max_length=5000,
        error_messages={
            "required": "Укажи описание вакансии.",
            "blank": "Описание вакансии не может быть пустым.",
            "min_length": "Описание должно быть не короче 20 символов.",
            "max_length": "Описание должно быть не длиннее 5000 символов.",
        },
    )
    location = serializers.CharField(
        min_length=2,
        max_length=120,
        error_messages={
            "required": "Укажи локацию.",
            "blank": "Локация не может быть пустой.",
            "min_length": "Локация должна быть не короче 2 символов.",
            "max_length": "Локация должна быть не длиннее 120 символов.",
        },
    )
    job_type = serializers.ChoiceField(
        choices=Job.JOB_TYPES,
        error_messages={"required": "Укажи тип вакансии.", "invalid_choice": "Выбери корректный тип вакансии."},
    )
    salary_min = serializers.IntegerField(
        required=False,
        allow_null=True,
        error_messages={"invalid": "Минимальная зарплата должна быть числом."},
    )
    salary_max = serializers.IntegerField(
        required=False,
        allow_null=True,
        error_messages={"invalid": "Максимальная зарплата должна быть числом."},
    )
    deadline = serializers.DateField(
        error_messages={"required": "Укажи дедлайн.", "invalid": "Введите корректную дату."}
    )

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "location",
            "job_type",
            "salary_min",
            "salary_max",
            "deadline",
            "is_active",
            "employer",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_deadline(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом.")
        return value

    def validate(self, attrs):
        salary_min = attrs.get("salary_min")
        salary_max = attrs.get("salary_max")

        if salary_min is not None and salary_min < 0:
            raise serializers.ValidationError({"salary_min": "Минимальная зарплата не может быть отрицательной."})
        if salary_max is not None and salary_max < 0:
            raise serializers.ValidationError({"salary_max": "Максимальная зарплата не может быть отрицательной."})
        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError(
                {
                    "salary_min": "Минимальная зарплата не может быть больше максимальной.",
                    "salary_max": "Максимальная зарплата не может быть меньше минимальной.",
                }
            )
        return attrs


class ApplicationSerializer(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.filter(is_active=True))
    full_name = serializers.CharField(
        min_length=3,
        max_length=120,
        error_messages={
            "required": "Укажи имя и фамилию.",
            "blank": "Имя и фамилия не могут быть пустыми.",
            "min_length": "Имя и фамилия должны быть не короче 3 символов.",
            "max_length": "Имя и фамилия должны быть не длиннее 120 символов.",
        },
    )
    email = serializers.EmailField(
        error_messages={"required": "Укажи email.", "invalid": "Введите корректный email."}
    )
    phone = serializers.CharField(
        min_length=7,
        max_length=20,
        error_messages={
            "required": "Укажи телефон.",
            "blank": "Телефон не может быть пустым.",
            "min_length": "Телефон слишком короткий.",
            "max_length": "Телефон слишком длинный.",
        },
    )
    cover_letter = serializers.CharField(
        min_length=50,
        max_length=5000,
        error_messages={
            "required": "Укажи сопроводительное письмо.",
            "blank": "Сопроводительное письмо не может быть пустым.",
            "min_length": "Сопроводительное письмо должно быть не короче 50 символов.",
            "max_length": "Сопроводительное письмо должно быть не длиннее 5000 символов.",
        },
    )
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "full_name",
            "email",
            "phone",
            "cover_letter",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]

    def validate_phone(self, value):
        allowed = set("0123456789+()- ")
        if any(ch not in allowed for ch in value):
            raise serializers.ValidationError("Телефон может содержать только цифры, пробелы, +, -, (, ).")
        return value

    def validate(self, attrs):
        job = attrs.get("job")
        email = attrs.get("email")

        if job and not job.is_active:
            raise serializers.ValidationError({"job": "Эта вакансия неактивна."})

        if job and email and Application.objects.filter(job=job, email__iexact=email).exists():
            raise serializers.ValidationError(
                {"email": "Вы уже отправляли заявку на эту вакансию."}
            )

        if job and job.deadline < timezone.localdate():
            raise serializers.ValidationError({"job": "Срок подачи на эту вакансию уже закончился."})

        return attrs