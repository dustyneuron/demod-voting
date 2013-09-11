from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from gitrepos.models import PullRequest
from voting.models import Change, Section

import sys
import json

class Command(BaseCommand):
    help = 'Creates pull request change(s) with JSON list read from stdin'
    
    def handle(self, *args, **options):
        js_data = ''
        for line in sys.stdin:
            js_data += line
        data = json.loads(js_data)
        
        for pr_data in data:
            pr = PullRequest(**PullRequest.init_args(pr_data))
            pr.save(force_insert=True)
            
            section = Section.objects.get(content_object=pr.repo)

            change = Change(content_object=pr)
            change.save()
            change.sections.add(section)
            
