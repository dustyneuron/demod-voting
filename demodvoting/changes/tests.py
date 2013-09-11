from django.test import TestCase

from gitrepos.models import *
from voting.models import *
from voting.tests import TestUtils

class SimpleTest(TestCase, TestUtils):
    def setUp(self):
        self.reset_utils()
        
    def test_simple(self):
        repo = GitRepo(**GitRepo.init_args({
            'name': 'democraticd',
            'branch': 'master',
            'html_url': 'https://github.com/democraticd/democraticd/tree/master',
            }))
        repo.save(force_insert=True)
        
        section = Section(content_object=repo)
        section.save()
        self.assertEqual(section.content_object.id, repo.id)
        
        pr_list = [
            {
                'repo': 'democraticd',
                'base_ref': 'master',
                'issue_id': 1,
                'title': 'Change everything to RED',
                'description': 'I really like red, blue is rubbish.',
                'html_url': 'https://github.com/democraticd/democraticd/pull/1',
            },
            {
                'repo': 'democraticd',
                'base_ref': 'master',
                'issue_id': 2,
                'title': 'Add a unicorn to the front page',
                'description': 'Unicorns are the bestest',
                'html_url': 'https://github.com/democraticd/democraticd/pull/2',
            },
            {
                'repo': 'democraticd',
                'base_ref': 'master',
                'issue_id': 8,
                'title': 'Wow what a lot of changes',
                'html_url': 'https://github.com/democraticd/democraticd/pull/8',
            },
            {
                'repo': 'democraticd',
                'base_ref': 'master',
                'issue_id': 666,
                'title': 'DESTROY SERVER',
                'description': 'I LOVE TO WATCH THINGS BURN',
                'html_url': 'https://github.com/democraticd/democraticd/pull/666',
            },
            ]
        
        change = {}
        for pr_data in pr_list:
            pr = PullRequest(**PullRequest.init_args(pr_data))
            pr.save(force_insert=True)
            self.assertEqual(pr.repo_id, repo.id)
            
            c = Change(content_object=pr)
            c.save()
            c.sections.add(section)
            self.assertEqual(c.content_object.id, pr.id)
            change[c.content_object.issue_id] = c
        
        u1, u2, u3, u4, u5 = self.voters(5)
        
        set_user_votes(u1, section, [change[1], change[2]])
        set_user_votes(u2, section, [change[8]])
        set_user_votes(u3, section, [change[2], change[1]])
        set_user_votes(u4, section, [change[8], change[2]])
        set_user_votes(u5, section, [change[666]])
        


