from django.test import TestCase

from voting.models import *
from voting.av import tie_break, find_winners
from django.contrib.auth.models import User

class TieBreaks(TestCase):
    def test_simple(self):
        c, p = tie_break([('c1', {1:2}), ('c2', {1:1, 2:10})])
        self.assertEqual((c, p), ('c1', {1:2}))

    def test_simple2(self):
        c, p = tie_break([('c1', {2:4}), ('c2', {1:1})])
        self.assertEqual((c, p), ('c2', {1:1}))

    def test_simple3(self):
        c, p = tie_break([('c1', {1:1, 2:1, 3:1, 4:4}), ('c2', {1:1, 2:1, 3:1, 4:4})])
        # will pick randomly
        self.assertEqual(p, {1:1, 2:1, 3:1, 4:4})

    def test_simple4(self):
        c, p = tie_break([('c1', {1:1, 2:1, 3:1, 4:4}), ('c2', {1:1, 2:1, 3:1, 4:0})])
        self.assertEqual((c, p), ('c1', {1:1, 2:1, 3:1, 4:4}))

    def test_simple5(self):
        c, p = tie_break([('c1', {10:1}), ('c2', {24:1}), ('c3', {100:1, 9:2})])
        self.assertEqual((c, p), ('c3', {100:1, 9:2}))

    def test_simple6(self):
        c, p = tie_break([('c1', {10:1}), ('c2', {24:1}), ('c3', {100:1, 9:2})])
        self.assertEqual((c, p), ('c3', {100:1, 9:2}))


class AVTests(TestCase):    
    def users(self, count):
        results = []
        for i in range(count):
            u = User(username='user' + str(self.user_inc))
            self.user_inc += 1
            u.save()
            results.append(u)
        if count > 1:
            return tuple(results)
        return results[0]
        
    def sections(self, count):
        results = []
        for i in range(count):
            u = Section(name='section' + str(self.section_inc))
            self.section_inc += 1
            u.save()
            results.append(u)
        if count > 1:
            return tuple(results)
        return results[0]
        
    def changes(self, count, *sections):
        results = []
        for i in range(count):
            u = Change(name='change' + str(self.change_inc))
            self.change_inc += 1
            u.save()
            for s in sections:
                u.sections.add(s)
            results.append(u)
        if count > 1:
            return tuple(results)
        return results[0]
        
    def setUp(self):
        self.user_inc = 1
        self.section_inc = 1
        self.change_inc = 1
    
    def test_av_simple(self):
        u1, u2, u3 = self.users(3)
        
        s1, s2, s3 = self.sections(3)

        fix1, fix2 = self.changes(2, s1)
        fix3 = self.changes(1, s1, s2, s3)
        
        set_user_votes(u1, s1, [fix1])
        set_user_votes(u2, s1, [fix2, fix3])
        set_user_votes(u3, s1, [fix3])
                
        winners = find_winners()
        self.assertEqual(len(winners), 1)
        change, prefs = winners[0]
        self.assertEqual((change.name, prefs), (fix3.name, {1:1, 2:1}))

    def test_av_two_competing_sections(self):
        u1, u2, u3, u4, u5 = self.users(5)
        s1, s2 = self.sections(2)
        fix1, fix2 = self.changes(2, s1, s2)

        for u in [u1, u2, u3, u4]:
            set_user_votes(u, s1, [fix1])
            set_user_votes(u, s2, [fix2])

        set_user_votes(u5, s1, [fix1, fix2])
        set_user_votes(u5, s2, [fix1, fix2])
                
        winners = find_winners()
        self.assertEqual(len(winners), 1)
        change, prefs = winners[0]
        self.assertEqual((change.name, prefs), (fix1.name, {1:5}))
        
    def test_av_no_winners(self):
        u1, u2, u3, u4, u5 = self.users(5)
        s1 = self.sections(1)
        f1, f2, f3 = self.changes(3, s1)

        for u in [u1, u2]:
            set_user_votes(u, s1, [f1])
        for u in [u3, u4]:
            set_user_votes(u, s1, [f2])
            
        set_user_votes(u5, s1, [f3])

        winners = find_winners()
        self.assertEqual(len(winners), 0)

    def test_av_priorities(self):
        u1, u2, u3, u4, u5 = self.users(5)
        s1 = self.sections(1)
        f1, f2, f3 = self.changes(3, s1)

        for u in [u1, u2]:
            set_user_votes(u, s1, [f1, f3])
        for u in [u3, u4]:
            set_user_votes(u, s1, [f2, f3])
            
        set_user_votes(u5, s1, [f3, f2])

        winners = find_winners()
        self.assertEqual(len(winners), 1)
        change, prefs = winners[0]
        self.assertEqual((change.name, prefs), (f2.name, {1:2, 2:1}))

    def test_av_priorities2(self):
        u1, u2, u3, u4, u5 = self.users(5)
        s1 = self.sections(1)
        f1, f2, f3, f4, f5, backup = self.changes(6, s1)

        set_user_votes(u1, s1, [f1, backup])
        set_user_votes(u2, s1, [f2, backup])
        set_user_votes(u3, s1, [f3, backup])
        set_user_votes(u4, s1, [f4, backup])
        set_user_votes(u5, s1, [f5, backup])
        
        winners = find_winners()
        # This is why the AV voting system sucks
        self.assertEqual(len(winners), 0)
