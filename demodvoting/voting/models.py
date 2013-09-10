from django.db import models
from django.contrib.auth.models import User
from django.db import transaction

class Section(models.Model):
    name = models.CharField(max_length=200)

    # Alternative vote implementation, TODO: optimize
    @transaction.commit_on_success
    def find_winner_av(self):
        win_threshold = User.objects.count() / 2
        
        changes = Change.objects.filter(sections=self)        
        first_votes = {}
        for c in changes:
            first_votes[c.id] = Vote.objects.filter(section=self, change=c, priority=1).count()

        while True:
            if len(first_votes) == 1:
                win_id, win_count = list(first_votes.items())[0]
                return (win_id, win_count, win_count >= win_threshold)
                
            lowest_count, lowest_c_id = None, None
            for c_id in first_votes.keys():
                if first_votes[c_id] >= win_threshold:
                    return (c_id, first_votes[c_id], True)
                    
                if (lowest_count == None) or (first_votes[c_id] < lowest_count):
                    lowest_count = first_votes[c_id]
                    lowest_c_id = c_id
            
            # eliminate lowest_c
            for orig_vote in Vote.objects.filter(section=self, change_id=lowest_c_id):
                alternates = Vote.objects.filter(user=orig_vote.user, section=self, priority__gt=orig_vote.priority)
                if len(alternates) > 0:
                    first_votes[alternates[0].change_id] += 1
            del first_votes[lowest_c_id]
            

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
