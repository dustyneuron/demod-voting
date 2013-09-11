from django.test import TestCase

from gitrepos.models import *

class SimpleTest(TestCase):
    def test_simple(self):
        r = GitRepo(**GitRepo.init_args({'name': 'democraticd', 'branch': 'master'}))
        r.save(force_insert=True)
        
        pr_data = {
                'repo': 'democraticd',
                'base_ref': 'master',
                'issue_id': 1,
            }
        pr = PullRequest(**PullRequest.init_args(pr_data))
        pr.save(force_insert=True)
        
        self.assertEqual(pr.repo_id, r.id)

