from django.db import models
from django.contrib.auth.models import User
from django.db import transaction

@transaction.commit_on_success
def find_winners_av():
    winners = {}
    sections = {}
    for section in Section.objects.all():
        sections[section] = []
        change, num_votes = section.find_winner_av()
        if change:
            print(section.name + ' winner is ' + change.name + ' (' + str(num_votes) + ' votes)')
            winners[change] = num_votes
        
    for change, num_votes in winners.items():
        for affected_section in change.sections.all():
            sections[affected_section].append((change, num_votes))
    
    final_winners = {}
    for section, change_list in sections.items():
        if change_list:
            #s = ' '.join([(change.name + ' (' + str(num_votes) + ' votes)') for (change, num_votes) in change_list])
            #print(section.name + ' winning changes are ' + s)
            change_list.sort(key=lambda x: x[1])
            change, num_votes = change_list.pop()
            final_winners[change] = num_votes
        
    return list(final_winners.items())
    

class Section(models.Model):
    name = models.CharField(max_length=200)

    def _av_tie_break(self, tuple_list, find_worst=False):
        if len(tuple_list) == 0:
            raise Exception('av tie break given empty list')
        
        all_pris = set([])
        dic = {}
        for change, av_data in tuple_list:
            counts = {}
            for v in Vote.objects.filter(section=self, change=change).all():
                if v.priority not in counts:
                    counts[v.priority] = 0
                counts[v.priority] += 1
            
            all_pris = all_pris.union(counts.keys())
            for p, n in counts.items():
                if p not in dic:
                    dic[p] = {'data':{}, 'nums':set([])}
                if n not in dic[p]['data']:
                    dic[p]['data'][n] = []
                    
                dic[p]['data'][n].append((change, av_data))
                dic[p]['nums'].add(n)
        
        all_pris = list(all_pris)    
        all_pris.sort()
                
        group = []
        all_best_first = []
        for p in all_pris:
            dic[p]['nums'] = list(dic[p]['nums'])
            dic[p]['nums'].sort()
            dic[p]['nums'].reverse()
                
            for n in dic[p]['nums']:
                group = dic[p]['data'][n]
                if find_worst:
                    all_best_first.append(group)
                elif len(group) == 1:
                    return group[0]
        
        if find_worst:
            group = all_best_first.pop()
        
        if len(group) == 1:
            return group[0]
        elif len(group) > 1:
            # TODO: random
            return group[0]
        raise Exception('AV tie break failed')
        

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
                top = [t for t in tuple_list if t[1] == highest_count]
                return self._av_tie_break(top)
            
            lowest_count = tuple_list[0][1]
            elim_cands = [t for t in tuple_list if t[1] == lowest_count]
            lowest_c, _ = self._av_tie_break(elim_cands, find_worst=True)
                        
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
