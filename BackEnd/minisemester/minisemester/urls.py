"""
URL configuration for minisemester project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings             # 1. 导入 settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("discussions/", include("discussions.urls")),  # 添加此行
    path("conversation/", include("discussions.urls")),  # 添加此行
    path("publications/", include("publications.urls")),  # 其他应用的 URL 保持不变
    path("documents/", include("document.urls")),  # 其他应用的 URL 保持不变

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)