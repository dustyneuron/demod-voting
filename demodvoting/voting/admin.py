from django.contrib import admin
from voting.models import Voter, Section, Change, Vote


admin.site.register(Voter)
admin.site.register(Section)
admin.site.register(Change)
admin.site.register(Vote)
