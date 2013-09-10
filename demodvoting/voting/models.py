from django.db import models
from django.db import transaction
from django.contrib.auth.models import User
    

class Section(models.Model):
    name = models.CharField(max_length=200)            

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
