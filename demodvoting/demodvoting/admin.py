from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from pullrequests.models import GitUser
from voting.models import Voter

# Define an inline admin descriptor for GitUser model
# which acts a bit like a singleton
class GitUserInline(admin.StackedInline):
    model = GitUser
    can_delete = False
    
class VoterInline(admin.StackedInline):
    model = Voter
    can_delete = False

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (GitUserInline, VoterInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

