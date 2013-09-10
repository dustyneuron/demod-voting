from django.contrib import admin
from pullrequests.models import GitUser, PullRequest

admin.site.register(PullRequest)
admin.site.register(GitUser)
