from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from pullrequests.models import PullRequest

import sys
import json

class Command(BaseCommand):
    help = 'Creates pull request(s) with JSON list read from stdin'
    
    def handle(self, *args, **options):
        js_data = ''
        for line in sys.stdin:
            js_data += line
        data = json.loads(js_data)
        
        for pr_data in data:
            pr = PullRequest(**PullRequest.init_args(pr_data))
            pr.save(force_insert=True)

            
