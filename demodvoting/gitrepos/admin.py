from django.contrib import admin
from gitrepos.models import GitUser, PullRequest

admin.site.register(PullRequest)
admin.site.register(GitUser)
