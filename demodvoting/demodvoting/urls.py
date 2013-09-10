from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
from demodvoting.admin import *

urlpatterns = patterns('',
    url(r'^pullrequests/', include('pullrequests.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
