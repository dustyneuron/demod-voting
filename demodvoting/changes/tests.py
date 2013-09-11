from django.test import TestCase

from gitrepos.models import *
from voting.models import *

class SimpleTest(TestCase):
    def test_simple(self):
        repo = GitRepo(**GitRepo.init_args({'name': 'democraticd', 'branch': 'master'}))
        repo.save(force_insert=True)
        
        section = Section(content_object=repo)
        section.save()
        self.assertEqual(section.content_object.id, repo.id)
        
        pr_data = {
                'repo': 'democraticd',
                'base_ref': 'master',
                'issue_id': 1,
            }
        pr = PullRequest(**PullRequest.init_args(pr_data))
        pr.save(force_insert=True)
        self.assertEqual(pr.repo_id, repo.id)
        
        change = Change(content_object=pr)
        change.save()
        change.sections.add(section)
        self.assertEqual(change.content_object.id, pr.id)
