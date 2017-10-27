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
from myproject import main, slack

urlpatterns = [
               url(r'^admin', include(admin.site.urls)),
               url(r'^poll', main.serve_poll),
               url(r'^left', main.left),
               url(r'^right', main.right),
               url(r'^in', main.zin),
               url(r'^out', main.out),
               url(r'^uri', main.uri),
               url(r'^up', main.up),
               url(r'^down', main.down),
               url(r'^pc', main.pc),
               url(r'^dial', main.dial),
               url(r'^hu', main.hu),
               url(r'^email', main.email),
               url(r'^zapcal', main.zapcal),
               url(r'^moxtra', main.moxtra),
               url(r'^ifttt/(?P<dn>[0-9]{4,15})@(?P<domain>[a-z0-9.]{3,30}))', main.ifttt),
               url(r'^nexmo_error', slack.nexmo_error),
               url(r'^nexmo_status', slack.nexmo_status),
               url(r'^nexmo_poll', slack.nexmo_poll),
               url(r'^nexmo/(?P<dn>[0-9]{4,10})/(?P<domain>[a-z0-9.]{3,30})', slack.nexmo_ans ),  #nothing to do with slack really
               url(r'^nexmo', slack.nexmo_ans),
               url(r'^slackpw', slack.slackpw),
               url(r'^slack', slack.slack),
               url(r'^page', slack.page),
               url(r'^', main.serve_blank)
]
