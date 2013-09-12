from django.shortcuts import render

from voting.models import Voter, Change, Section, Vote

def index(request):
    num_voters = Voter.count_eligible()
    sections = Section.objects.all()
    for s in sections:
        s.threshold = num_voters * s.majority_for_change
        s.cached_cs = []
        for c in s.change_set.all():
            c.prefs = c.do_count(s.id, add_zeros=True)
            s.cached_cs.append(c)
    return render(request, 'changes/index.html', {
        'sections': sections,
        'github_name': 'democraticd',
        'num_voters': num_voters,
        })
