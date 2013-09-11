from django.db import models
from django.contrib.auth.models import User

class GitUser(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    github_name = models.CharField(max_length=100, unique=True)
    
class GitRepo(models.Model):
    repo = models.CharField(max_length=200)
    branch = models.CharField(max_length=200)
    
    @classmethod
    def init_args(cls, pr_data):
        fields = [f.name for f in cls._meta.fields]
        args = {}
        for f in fields:
            args[f] = pr_data[f]
        return args
        
    class Meta:
        ordering = ['repo', 'branch']
        unique_together = (('repo', 'branch'),)

class PullRequest(models.Model):
    key = models.CharField(primary_key=True, max_length=200)
    git_user = models.ForeignKey(GitUser, blank=True, null=True)
        
    issue_id = models.IntegerField(default=0)
    title = models.CharField(max_length=200)
    description = models.TextField()
    state = models.IntegerField(default=0)
    
    repo = models.ForeignKey(GitRepo)
    base_sha = models.CharField(max_length=64)
    
    ref = models.CharField(max_length=200)
    sha = models.CharField(max_length=64)
    
    def __str__(self):
        return self.key + ' state ' + str(self.state)
        
    @classmethod
    def init_args(cls, pr_data):
        fields = [f.name for f in cls._meta.fields]
        fields.remove('git_user')
        fields.remove('key')
        fields.remove('repo')
        fields.remove('base_ref')
        args = {}
        for f in fields:
            args[f] = pr_data[f]
            
        #args['git_user'] = GitUser.objects.get(github_name=pr_data['username'])
        args['repo'] = GitRepo.objects.get(repo=pr_data['repo'], branch=pr_data['base_ref'])
        args['key'] = cls.create_key(pr_data)
        return args

    @classmethod
    def create_key(cls, pr_data):
        return 'github/' + pr_data['repo'] + '/' + str(pr_data['issue_id'])


