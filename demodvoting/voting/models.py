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
            winners[change] = num_votes
        
    for change, num_votes in winners.items():
        for affected_section in change.sections.all():
            sections[affected_section].append((change, num_votes))
    
    final_winners = {}
    for section, change_list in sections.items():
        #s = ' '.join([(change.name + ' (' + str(num_votes) + ' votes)') for (change, num_votes) in change_list])
        #print(section.name + ' winning changes are ' + s)
        change_list.sort(key=lambda x: x[1])
        change, num_votes = change_list.pop()
        final_winners[change] = num_votes
        
    return list(final_winners.items())
        

class Section(models.Model):
    name = models.CharField(max_length=200)

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
            for c in first_votes.keys():
                if first_votes[c] >= win_threshold:
                    return (c, first_votes[c])
                    
                if (lowest_count == None) or (first_votes[c] < lowest_count):
                    lowest_count = first_votes[c]
                    lowest_c = c
            
            # eliminate lowest_c
            for orig_vote in Vote.objects.filter(section=self, change=lowest_c):
                alternates = Vote.objects.filter(user=orig_vote.user, section=self, priority__gt=orig_vote.priority)
                if len(alternates) > 0:
                    first_votes[alternates[0].change] += 1
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
