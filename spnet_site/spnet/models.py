from django.db import models
from django.contrib.auth.models import User # User model from the Authentication system
# see https://docs.djangoproject.com/en/1.3/topics/auth/

# see http://www.djangobook.com/en/1.0/chapter12/#cn222
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    datetime_joined = models.DateTimeField()
    datetime_last_seen = models.DateTimeField()
    followers = models.ManyToMany(User)
    following = models.ManyToMany(User)
    
class Author(models.Model):
    name = models.CharField(max_length=1000)
    email =  models.CharField(max_length=1000) # is there a max length for emails?
    papers = models.ManyToMany(Author)
    user = models.ForeignKey(User, unique=True) # is this author a user?
    
class Paper(models.Model):
    arxiv_identifier = models.CharField(max_length=50) # should check if these are well-defined by ArXiv
    authors = models.ManyToMany(Author)
    title = models.CharField(max_length=1000)
    topic_groups = models.ManyToMany(TopicGroup)
    submitter = models.ForeignKey(User)
    #comment_threads

class Recommendation(models.Model):
    recommender = models.ForeignKey(User)
    paper = models.ForiegnKey(Paper)
    has_review = models.BooleanField()
    review_text = models.TextField()
    datetime = models.DateTimeField()

class TopicGroup(models.Model):
    name = models.CharField(max_length=200)
    papers = models.ManyToMany(Paper)
    users = models.ManyToMany(User)

# Comments: http://codeblogging.net/blogs/1/3/    
