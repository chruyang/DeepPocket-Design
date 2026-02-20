from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from pipeline import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),          # 首页
    path('api/run', views.run_pipeline, name='run'), # API 接口
]

# 允许开发环境下访问 media 文件 (下载结果用)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)