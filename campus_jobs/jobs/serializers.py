from django.utils import timezone
from rest_framework import serializers

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


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ["id", "name", "code"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Название факультета должно быть не короче 2 символов.")
        return value


class DepartmentSerializer(serializers.ModelSerializer):
    faculty = serializers.PrimaryKeyRelatedField(queryset=Faculty.objects.all())

    class Meta:
        model = Department
        fields = ["id", "faculty", "name"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Название кафедры должно быть не короче 2 символов.")
        return value

    def validate(self, attrs):
        faculty = attrs.get("faculty")
        name = attrs.get("name")
        if faculty and name and Department.objects.filter(faculty=faculty, name__iexact=name).exists():
            raise serializers.ValidationError({"name": "Такая кафедра уже существует на этом факультете."})
        return attrs


class EmployerSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Employer
        fields = ["id", "name", "contact_email", "department", "description", "website"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Название работодателя должно быть не короче 2 символов.")
        return value


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ["id", "name", "slug"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Название категории должно быть не короче 2 символов.")
        return value


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Название навыка должно быть не короче 2 символов.")
        return value


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = [
            "id",
            "student_full_name",
            "student_email",
            "phone",
            "title",
            "summary",
            "file_name",
            "is_primary",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_student_full_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Имя студента должно быть не короче 3 символов.")
        return value

    def validate_summary(self, value):
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError("Описание резюме должно быть не короче 20 символов.")
        return value


class JobSerializer(serializers.ModelSerializer):
    employer = serializers.PrimaryKeyRelatedField(queryset=Employer.objects.all())
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False, allow_null=True)
    category = serializers.PrimaryKeyRelatedField(queryset=JobCategory.objects.all(), required=False, allow_null=True)
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        write_only=True,
    )
    skills = serializers.SerializerMethodField(read_only=True)

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
            "department",
            "category",
            "skill_ids",
            "skills",
            "created_at",
        ]
        read_only_fields = ["created_at", "skills"]

    def get_skills(self, obj):
        return [
            {
                "id": js.skill_id,
                "name": js.skill.name,
                "required_level": js.required_level,
            }
            for js in obj.job_skills.select_related("skill").all()
        ]

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 5:
            raise serializers.ValidationError("Название вакансии должно быть не короче 5 символов.")
        return value

    def validate_description(self, value):
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError("Описание вакансии должно быть не короче 20 символов.")
        return value

    def validate_deadline(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом.")
        return value

    def validate_skill_ids(self, value):
        unique_ids = set(value)
        if len(unique_ids) != len(value):
            raise serializers.ValidationError("Список навыков содержит дубликаты.")

        existing_count = Skill.objects.filter(id__in=unique_ids).count()
        if existing_count != len(unique_ids):
            raise serializers.ValidationError("Один или несколько навыков не найдены.")
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

    def _apply_skills(self, job, skill_ids):
        if skill_ids is None:
            return

        job.job_skills.all().delete()
        for skill in Skill.objects.filter(id__in=skill_ids):
            JobSkill.objects.create(job=job, skill=skill, required_level=JobSkill.RequiredLevel.BASIC)

    def create(self, validated_data):
        skill_ids = validated_data.pop("skill_ids", [])
        job = super().create(validated_data)
        self._apply_skills(job, skill_ids)
        return job

    def update(self, instance, validated_data):
        skill_ids = validated_data.pop("skill_ids", None)
        job = super().update(instance, validated_data)
        self._apply_skills(job, skill_ids)
        return job


class JobSkillSerializer(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    skill = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all())

    class Meta:
        model = JobSkill
        fields = ["id", "job", "skill", "required_level"]

    def validate(self, attrs):
        job = attrs.get("job")
        skill = attrs.get("skill")
        if job and skill and JobSkill.objects.filter(job=job, skill=skill).exists():
            raise serializers.ValidationError({"skill": "Этот навык уже добавлен к вакансии."})
        return attrs


class ApplicationSerializer(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.filter(is_active=True))
    resume = serializers.PrimaryKeyRelatedField(queryset=Resume.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "resume",
            "full_name",
            "email",
            "phone",
            "cover_letter",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]

    def validate_full_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Имя и фамилия должны быть не короче 3 символов.")
        return value

    def validate_phone(self, value):
        allowed = set("0123456789+()- ")
        if any(ch not in allowed for ch in value):
            raise serializers.ValidationError("Телефон может содержать только цифры, пробелы, +, -, (, ).")
        return value

    def validate_cover_letter(self, value):
        value = value.strip()
        if len(value) < 50:
            raise serializers.ValidationError("Сопроводительное письмо должно быть не короче 50 символов.")
        return value

    def validate(self, attrs):
        job = attrs.get("job")
        email = attrs.get("email")
        resume = attrs.get("resume")

        if job and email and Application.objects.filter(job=job, email__iexact=email).exists():
            raise serializers.ValidationError({"email": "Вы уже отправляли заявку на эту вакансию."})

        if resume and email and resume.student_email.lower() != email.lower():
            raise serializers.ValidationError({"resume": "Email в резюме должен совпадать с email заявки."})

        if job and job.deadline < timezone.localdate():
            raise serializers.ValidationError({"job": "Срок подачи на эту вакансию уже закончился."})

        return attrs


class InterviewSerializer(serializers.ModelSerializer):
    application = serializers.PrimaryKeyRelatedField(queryset=Application.objects.all())

    class Meta:
        model = Interview
        fields = ["id", "application", "scheduled_at", "location", "status", "notes"]

    def validate_scheduled_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Дата и время интервью должны быть в будущем.")
        return value

    def validate_location(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Укажи корректное место проведения интервью.")
        return value