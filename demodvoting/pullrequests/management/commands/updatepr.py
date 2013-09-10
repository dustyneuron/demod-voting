from django.core.management.base import BaseCommand, CommandError
from pullrequests.models import PullRequests, pr_key

class Command(BaseCommand):
    help = 'Updates/adds pull request(s) with JSON list read from stdin'

    def handle(self, *args, **options):
        js_data = ''
        for line in self.stdin:
            js_data += line
        data = json.loads(js_data)
        
        for pr_data in data:
            key = pr_key(pr_data)
            pr = None
            try:
                pr = PullRequests.objects.get(pk=key)
            except Poll.DoesNotExist:
                pr = PullRequests()

            poll.opened = False
            poll.save()

            self.stdout.write('Successfully closed poll "%s"' % poll_id)
