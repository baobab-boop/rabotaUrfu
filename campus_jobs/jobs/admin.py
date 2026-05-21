from django.contrib import admin

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


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 0
    autocomplete_fields = ["skill"]


class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0
    readonly_fields = ("created_at", "updated_at")


class InterviewInline(admin.TabularInline):
    model = Interview
    extra = 0


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "faculty")
    list_filter = ("faculty",)
    search_fields = ("name", "faculty__name", "faculty__code")
    autocomplete_fields = ["faculty"]


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "department")
    list_filter = ("department",)
    search_fields = ("name", "contact_email")
    autocomplete_fields = ["department"]


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "employer", "department", "category", "job_type", "deadline", "is_active")
    list_filter = ("job_type", "is_active", "category", "department")
    search_fields = ("title", "description", "location", "employer__name")
    autocomplete_fields = ["employer", "department", "category"]
    inlines = [JobSkillInline, ApplicationInline]


@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    list_display = ("job", "skill", "required_level")
    list_filter = ("required_level",)
    search_fields = ("job__title", "skill__name")
    autocomplete_fields = ["job", "skill"]


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("student_full_name", "student_email", "title", "is_primary", "created_at")
    list_filter = ("is_primary",)
    search_fields = ("student_full_name", "student_email", "title")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "job", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("full_name", "email", "job__title")
    autocomplete_fields = ["job", "resume"]
    readonly_fields = ("created_at", "updated_at")
    inlines = [InterviewInline]


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("application", "scheduled_at", "status", "location")
    list_filter = ("status",)
    search_fields = ("application__full_name", "application__job__title", "location")
    autocomplete_fields = ["application"]

admin.site.site_header = "Campus Jobs Администрирование"
admin.site.site_title = "Campus Jobs"
admin.site.index_title = "Панель управления"