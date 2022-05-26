"""monitorias URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views as auth_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerSplitView
import core
from core.views import CursoViewSet

from core.views import CursoViewSet

router = routers.DefaultRouter()
router.register(r"cursos", CursoViewSet, basename="cursos")


router.register(r"cursos", CursoViewSet, basename="cursos")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", auth_views.obtain_auth_token, name="obtain-api-token"),
    path("", include(router.urls)),
    path("cursos/add/", include("core.urls")),
    # documentação/drf_spectacular
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/openapi/",
        SpectacularSwaggerSplitView.as_view(url_name="schema"),
        name="openapi",
    ),
]
