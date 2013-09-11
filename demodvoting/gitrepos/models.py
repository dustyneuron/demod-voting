from django.db import models
from django.contrib.auth.models import User

def init_args(cls, pr_data):
    fields = [f.name for f in cls._meta.fields]
    args = {}
    for f in fields:
        if f in pr_data:
            args[f] = pr_data[f]
    return args


class GitUser(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    github_name = models.CharField(max_length=100, unique=True)
    
class GitRepo(models.Model):
    name = models.CharField(max_length=200)
    branch = models.CharField(max_length=200)
    
    description = models.CharField(max_length=200)
    html_url = models.URLField()
    
    @classmethod
    def init_args(cls, r_data):
        return init_args(cls, r_data)
        
    class Meta:
        ordering = ['name', 'branch']
        unique_together = (('name', 'branch'),)

class PullRequest(models.Model):
    id = models.CharField(primary_key=True, max_length=200)
    git_user = models.ForeignKey(GitUser, blank=True, null=True)
        
    issue_id = models.IntegerField(default=0)
    title = models.CharField(max_length=200)
    description = models.TextField()
    html_url = models.URLField()
    
    state = models.IntegerField(default=0)
    
    repo = models.ForeignKey(GitRepo)
    base_sha = models.CharField(max_length=64)
    
    ref = models.CharField(max_length=200)
    sha = models.CharField(max_length=64)
    
    def __str__(self):
        return self.key + ' state ' + str(self.state)
        
    @classmethod
    def init_args(cls, pr_data):
        args = init_args(cls, pr_data)
        try:
            del args['git_user']
        except KeyError:
            pass
        args['id'] = cls.create_key(pr_data)
        #args['git_user'] = GitUser.objects.get(github_name=pr_data['username'])
        args['repo'] = GitRepo.objects.get(name=pr_data['repo'], branch=pr_data['base_ref'])
        return args

    @classmethod
    def create_key(cls, pr_data):
        return 'github/' + pr_data['repo'] + ' issue #' + str(pr_data['issue_id'])


