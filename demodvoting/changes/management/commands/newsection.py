from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from gitrepos.models import GitRepo

import sys
import json

class Command(BaseCommand):
    help = 'Creates git repos(s) with JSON list read from stdin'
    
    def handle(self, *args, **options):
        js_data = ''
        for line in sys.stdin:
            js_data += line
        data = json.loads(js_data)
        
        for repo_data in data:
            repo = GitRepo(**GitRepo.init_args(repo_data))
            repo.save(force_insert=True)
            
            section = Section(content_object=repo)
            section.save()
            
