from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/vacancies/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('vacancies/', include('vacancies.urls')),
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
