"""iico URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    url(r'^plat/', views.index, name='index'),
    url(r'^$', views.index_login, name='login'),
    url(r'^login/', views.index_login, name='login'),
    url(r'^reg/', views.reg, name='reg'),
    url(r'^regin/', views.regin, name='regin'),
    url(r'^update/', views.post),
    url(r'^signin/', views.signin, name='signin'),
]

urlpatterns+=staticfiles_urlpatterns()


