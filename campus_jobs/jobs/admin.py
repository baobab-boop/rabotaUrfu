from django.contrib import admin

from .models import Application, Employer, Job


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "website")
    search_fields = ("name", "contact_email")


class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    fields = ("full_name", "email", "phone", "status", "created_at")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "employer", "job_type", "location", "deadline", "is_active", "created_at")
    list_filter = ("job_type", "is_active", "location")
    search_fields = ("title", "description", "location", "employer__name")
    inlines = [ApplicationInline]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "job", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("full_name", "email", "job__title")
    readonly_fields = ("created_at", "updated_at")