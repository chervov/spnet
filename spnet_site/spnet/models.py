from datetime import datetime
from django.db import models
from django.contrib.auth.models import User # User model from the Authentication system
# see https://docs.djangoproject.com/en/1.3/topics/auth/

class TopicGroup(models.Model):
    name = models.CharField(max_length=200)
    definition = models.TextField()
    creator = models.ForeignKey(User)
    datetime_created = models.DateTimeField(default=datetime.now)

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name='subscriptions_in')
    recommender = models.ForeignKey(User, related_name='subscriptions_out')
    request_all = models.BooleanField() # get all recs, regardless of topic
    datetime_created = models.DateTimeField(default=datetime.now)

# see http://www.djangobook.com/en/1.0/chapter12/#cn222
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    datetime_joined = models.DateTimeField(default=datetime.now)
    datetime_last_seen = models.DateTimeField()
    recommenders = models.ManyToManyField(User, through='Subscription',
                                     symmetrical=False,
                                     related_name='subscribers')
    topic_groups = models.ManyToManyField(TopicGroup, related_name='members')
    
class Author(models.Model):
    name = models.CharField(max_length=1000)
    email =  models.CharField(max_length=1000) # is there a max length for emails?
    papers = models.ManyToManyField('Paper', related_name='authors')
    user = models.ForeignKey(User, unique=True) # is this author a user?

class PaperDB(models.Model):
    name = models.CharField(max_length=1000)
    url_template = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000)
    
    
class Paper(models.Model):
    paper_db = models.ForeignKey(PaperDB, related_name='papers')
    paper_id = models.CharField(max_length=50) # for generality, make it longer
    url_data = models.CharField(max_length=1000) # additional data for URL construction
    title = models.CharField(max_length=1000)
    topic_groups = models.ManyToManyField(TopicGroup,
                                          related_name='papers')
    submitter = models.ForeignKey(User, related_name='submissions')
    #comment_threads

class Recommendation(models.Model):
    recommender = models.ForeignKey(User, related_name='recommendations')
    paper = models.ForeignKey(Paper, related_name='recommendations')
    must_read = models.BooleanField() # highest level of rec
    private = models.BooleanField() # don't display this rec
    topic_groups = models.ManyToManyField(TopicGroup,
                                          related_name='recommendations')
    has_review = models.BooleanField()
    review_text = models.TextField()
    datetime_created = models.DateTimeField(default=datetime.now)


# Comments: http://codeblogging.net/blogs/1/3/    
