from django.test import TestCase

from voting.models import *
from django.contrib.auth.models import User

class AVTest(TestCase):
    def test_av_simple(self):
        fred = User(username='fred')
        fred.save()
        bob = User(username='bob')
        bob.save()
        dave = User(username='dave')
        dave.save()

        core_section = Section(name='core_code')
        core_section.save()
        util_section = Section(name='util_code')
        util_section.save()
        html_section = Section(name='html_code')
        html_section.save()

        html_fix1 = Change(name='html_fix1')
        html_fix1.save()
        html_fix1.sections.add(html_section)

        html_fix2 = Change(name='html_fix2')
        html_fix2.save()
        html_fix2.sections.add(html_section)

        massive_fix = Change(name='massive_fix')
        massive_fix.save()
        massive_fix.sections.add(core_section, util_section, html_section)

        set_user_votes(fred, html_section, [html_fix1])
        set_user_votes(bob, html_section, [html_fix2, massive_fix])
        set_user_votes(dave, html_section, [massive_fix])
                
        r = html_section.find_winner_av()

        self.assertEqual(r, (3, 2, True))
