from django.shortcuts import render

from voting.models import Voter, Change, Section, Vote

def index(request):
    sections = Section.objects.all()
    for s in sections:
        s.cached_cs = []
        for c in s.change_set.all():
            c.prefs = c.do_count(s.id)
            s.cached_cs.append(c)
    return render(request, 'changes/index.html', {'sections': sections, 'github_name': 'democraticd'})
