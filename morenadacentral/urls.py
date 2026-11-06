from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("apps.danzarines.urls")),
    path("", include("apps.bloques.urls")),
    path("", include("apps.inicio.urls")),
    path("", include("apps.historia.urls")),
    path("", include("apps.presidentes.urls")),
    path("", include("apps.directorio.urls")),
    path("", include("apps.reportes.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
