"""
URL configuration for DYNpocketback project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from Mainapp import views

urlpatterns = [
                  path("admin/", admin.site.urls),

                  path("login/", views.login),
                  path("logout/", views.logout),
                  path("home/", views.home),
                  path("search/", views.searchHtml),
                  path("prediction/", views.prediction),
                  path("help/", views.help),
                  path("user/", views.user),
                  path("register/",views.register),
                  path("add/user/", views.add_user),
                  path("index/", views.index),

                  path("searchPDB_searchimg", views.search_img),
                  path("searchPDB_download", views.search_pdb),
                  path("searchPDB", views.search),
                  path("upload/", views.upload_file),
                  path("download/", views.download_file),
                  path("getID/", views.getID),
                  path("txtDownload/", views.txt_download),
                  # path("send3D/", views.send_3Dfile),
                  path("cs/", views.cs),
                  path("prediction_out/", views.predict),

                  path('items/', views.item_list, name='item_list'),
                  path('testpost', views.testpost),
                  path('t/', views.model_invocation),

              ] + static("/", document_root="./Mainapp/templates/DynPocket")
