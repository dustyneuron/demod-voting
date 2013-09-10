from django.db import models
from django.contrib.auth.models import User
from django.db import transaction

import random

import voting.av

@transaction.commit_on_success
def find_winners_av():
    winners = {}
    sections = {}
    for section in Section.objects.all():
        sections[section] = []
        change, prefs = section.find_winner_av()
        if change:
            #print(section.name + ' winner is ' + change.name + ' (votes: ' + str(prefs) + ')')
            winners[change] = prefs
        else:
            #print(section.name + ' had no winner')
            pass
        
    for change, prefs in winners.items():
        for affected_section in change.sections.all():
            sections[affected_section].append((change, prefs))
    
    final_winners = {}
    for section, change_tuples in sections.items():
        if change_tuples:
            change, prefs = voting.av.tie_break(change_tuples)
            if change not in final_winners:
                final_winners[change] = []
            final_winners[change].append((change, prefs))
            
    # if one change is the winner in several sections,
    # return the highest scoring prefs
    for change, change_tuples in final_winners.items():
        _, prefs = voting.av.tie_break(change_tuples)
        if not prefs:
            raise Exception('prefs battling between identical changes failed')
        final_winners[change] = prefs
        
    return list(final_winners.items())
    

class Section(models.Model):
    name = models.CharField(max_length=200)

    def _section_tie_break(self, change_list, find_worst=False):
        if len(change_list) == 0:
            raise Exception('av tie break given empty change_list')
            
        #print('section tie break: ' + ' '.join([c.name for c in change_list]))
        
        change_tuples = []
        for change in change_list:
            prefs = {}
            for v in Vote.objects.filter(section=self, change=change).all():
                if v.priority not in prefs:
                    prefs[v.priority] = 0
                prefs[v.priority] += 1
                
            change_tuples.append((change, prefs))
            
        #print('section tie break: ' + str(change_tuples))
        
        return voting.av.tie_break(change_tuples, find_worst)
        

    # Alternative vote implementation, TODO: optimize
    @transaction.commit_on_success
    def find_winner_av(self):
        win_threshold = User.objects.count() / 2
        
        changes = Change.objects.filter(sections=self)    
        first_votes = {}
        for c in changes:
            first_votes[c] = Vote.objects.filter(section=self, change=c, priority=1).count()

        while True:                
            lowest_count, lowest_c = None, None
            tuple_list = list(first_votes.items())
            tuple_list.sort(key=lambda x: x[1])
            
            highest_count = tuple_list[len(tuple_list)-1][1]
            if highest_count >= win_threshold:
                top = [t[0] for t in tuple_list if t[1] == highest_count]
                return self._section_tie_break(top)
            
            lowest_count = tuple_list[0][1]
            elim_cands = [t[0] for t in tuple_list if t[1] == lowest_count]
            lowest_c, _ = self._section_tie_break(elim_cands, find_worst=True)
                        
            # re-assign votes for lowest_c to next pref
            for orig_vote in Vote.objects.filter(section=self, change=lowest_c):
                alternates = Vote.objects.filter(user=orig_vote.user, section=self, priority__gt=orig_vote.priority)
                if len(alternates) > 0:
                    alt = alternates[0].change
                    if alt not in first_votes:
                        first_votes[alt] = 0
                    first_votes[alt] += 1
            
            # eliminate lowest_c
            del first_votes[lowest_c]
            
            if len(first_votes) == 0:
                return (None, None)
            

class Change(models.Model):
    name = models.CharField(max_length=200)
    sections = models.ManyToManyField(Section)

class Vote(models.Model):
    user = models.ForeignKey(User)
    section = models.ForeignKey(Section)
    
    change = models.ForeignKey(Change)
    priority = models.IntegerField(default=1)
    
    
    class Meta:
        ordering = ['user', 'section', 'change', 'priority']
        unique_together = (
            ('user', 'section', 'change'),
            ('user', 'section', 'priority'),
            )

@transaction.commit_on_success
def set_user_votes(user, section, ordered_changes):
    Vote.objects.filter(user=user, section=section).delete()
    priority = 1
    for c in ordered_changes:
        if not c.sections.filter(pk=section.pk).exists():
            raise Exception('change section invalid - ' + str(list(c.sections.all())))
            
        Vote(user=user, section=section, change=c, priority=priority).save()
        priority += 1
