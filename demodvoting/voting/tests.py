from django.test import TestCase

from voting.models import *
from django.contrib.auth.models import User

class AVTest(TestCase):
    def users(self, count):
        results = []
        for i in range(count):
            u = User(username='user' + str(i))
            u.save()
            results.append(u)
        return tuple(results)
        
    def sections(self, count):
        results = []
        for i in range(count):
            u = Section(name='section' + str(i))
            u.save()
            results.append(u)
        return tuple(results)
    
    def test_av_simple(self):
        u1, u2, u3 = self.users(3)
        
        core_section, util_section, html_section = self.sections(3)

        html_fix1 = Change(name='html_fix1')
        html_fix1.save()
        html_fix1.sections.add(html_section)

        html_fix2 = Change(name='html_fix2')
        html_fix2.save()
        html_fix2.sections.add(html_section)

        massive_fix = Change(name='massive_fix')
        massive_fix.save()
        massive_fix.sections.add(core_section, util_section, html_section)

        set_user_votes(u1, html_section, [html_fix1])
        set_user_votes(u2, html_section, [html_fix2, massive_fix])
        set_user_votes(u3, html_section, [massive_fix])
                
        winners = find_winners_av()
        self.assertEqual(len(winners), 1)
        change, num_votes = winners[0]
        self.assertEqual((change.name, num_votes), ('massive_fix', 2))

    def test_av_two_competing_sections(self):
        u1, u2, u3, u4, u5 = self.users(5)
        s1, s2 = self.sections(2)

        fix1 = Change(name='fix1')
        fix1.save()
        fix1.sections.add(s1, s2)
        
        fix2 = Change(name='fix2')
        fix2.save()
        fix2.sections.add(s1, s2)

        for u in [u1, u2, u3, u4]:
            set_user_votes(u, s1, [fix1])
            set_user_votes(u, s2, [fix2])

        set_user_votes(u5, s1, [fix1, fix2])
        set_user_votes(u5, s2, [fix1, fix2])
                
        winners = find_winners_av()
        self.assertEqual(len(winners), 1)
        change, num_votes = winners[0]
        self.assertEqual((change.name, num_votes), ('fix1', 5))
