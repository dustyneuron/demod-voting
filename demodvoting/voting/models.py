from django.db import models
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Voter(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    
    def __str__(self):
        return '<Voter ' + str(self.user.username) + '>'

class Section(models.Model):
    name = models.CharField(max_length=200)            

class Change(models.Model):
    name = models.CharField(max_length=200)
    sections = models.ManyToManyField(Section)
    
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.CharField(max_length=200)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
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

@transaction.commit_on_success
def set_user_votes(voter, section, ordered_changes):
    Vote.objects.filter(voter=voter, section=section).delete()
    priority = 1
    for c in ordered_changes:
        if not c.sections.filter(pk=section.pk).exists():
            raise Exception('change section invalid - ' + str(list(c.sections.all())))
            
        Vote(voter=voter, section=section, change=c, priority=priority).save()
        priority += 1
