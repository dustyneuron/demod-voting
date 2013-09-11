from django.conf.urls import patterns, url

from changes import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)
