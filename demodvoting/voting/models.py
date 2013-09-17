from django.db import models
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.db.models import signals
from django.dispatch import receiver

def add_voter_hook(sender, **kwargs):
    if kwargs.get('raw') or not kwargs.get('created'):
        return
    u = kwargs['instance']
    Voter(user=u).save()

signals.post_save.connect(add_voter_hook, sender=User, dispatch_uid="add_voter_hook_id")

class Voter(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    has_vote = models.BooleanField(default=True)
    
    def __str__(self):
        return '<Voter ' + str(self.user.username) + '>'
    
    @classmethod
    def count_eligible(cls):
        return cls.objects.filter(has_vote=True).count()

class Section(models.Model):
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.CharField(max_length=200)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    majority_for_change = models.FloatField(default=0.5)
    
    class Meta:
        unique_together = (('content_type', 'object_id'),)

class Change(models.Model):
    sections = models.ManyToManyField(Section)
    
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.CharField(max_length=200)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = (('content_type', 'object_id'),)
        
    def do_count(self, section_id, priority=None, add_zeros=False):
        return Vote.do_count(section_id, self.id, priority, add_zeros)

    
class Vote(models.Model):
    voter = models.ForeignKey(Voter)
    section = models.ForeignKey(Section)
    
    change = models.ForeignKey(Change)
    priority = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['voter', 'section', 'change', 'priority']
        unique_together = (
            ('voter', 'section', 'change'),
            ('voter', 'section', 'priority'),
            )
        index_together = [
            ["section", "change", "priority"],
            ]
    
    @classmethod
    def do_count(cls, section_id, change_id, priority=None, add_zeros=False):
        if priority:
            return cls.objects.filter(section_id=section_id, change_id=change_id, priority=priority).count()
        
        prefs = {}
        max_pri = 0
        all_votes = cls.objects.filter(section_id=section_id, change_id=change_id)
        p_list = all_votes.order_by('priority').values_list('priority', flat=True).distinct()
        for p in p_list:
            prefs[p] = all_votes.filter(priority=p).count()
            max_pri = max(p, max_pri)
        if add_zeros:
            for n in range(1, max_pri):
                if n not in prefs:
                    prefs[n] = 0
        return prefs        
        


@transaction.commit_on_success
def set_user_votes(voter, section, ordered_changes):
    Vote.objects.filter(voter=voter, section=section).delete()
    
    vote_list = []
    for p, c in enumerate(ordered_changes, 1):
        if not c.sections.filter(pk=section.pk).exists():
            raise Exception('change section invalid - ' + str(list(c.sections.all())))

        vote_list.append(Vote(voter=voter, section=section, change=c, priority=p))
        
    Vote.objects.bulk_create(vote_list)
