"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from myproject import main

urlpatterns = [
               url(r'^admin/', include(admin.site.urls)),
               url(r'^poll', main.serve_poll),
               url(r'^left', main.left),
               url(r'^right', main.right),
               url(r'^in', main.zin),
               url(r'^out', main.out),
               url(r'^up', main.up),
               url(r'^down', main.down),
               url(r'^pc', main.pc),
               url(r'^email', main.email),
               url(r'^', main.serve_blank)
]
