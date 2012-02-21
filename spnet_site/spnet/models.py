from datetime import datetime
from django.db import models
from django.contrib.auth.models import User # User model from the Authentication system
# see https://docs.djangoproject.com/en/1.3/topics/auth/
from mptt.models import MPTTModel, TreeForeignKey

class TopicGroup(models.Model):
    '''allows anyone to define a topic:
    Has mappings to many kinds of data via the following attributes:

    members: all users who are interested in this topic.
    papers: all papers that claim to address this topic.
    recommendations: all recommendations addressed to this topic.

    Additional mappings for topic merging:
    merged_to: list of requests to merge this topic into another.
    merge_from: list of requests to merge another topic into this one.
    '''
    name = models.CharField(max_length=200)
    definition = models.TextField()
    creator = models.ForeignKey(User)
    datetime_created = models.DateTimeField(default=datetime.now)

class TopicMerge(models.Model):
    '''allows anyone to merge one topic into another for their
    own viewing.

    The system would presumably define a threshold percentage
    of members requesting a merge that would make that merge the
    default view.  In that case, a user can explicitly prevent
    the merge (for his own viewing) by setting the block_merger flag.'''
    user = models.ForeignKey(User, related_name='merge_requests')
    merge_from = models.ForeignKey(TopicGroup, related_name='merged_to')
    merged_to = models.ForeignKey(TopicGroup, related_name='merge_from')
    block_merger = models.BooleanField(default=False)

SUBSCRIPTION_PRIORITY_CHOICES = (
    (0, 'High'),
    (1, 'Medium'),
    (2, 'Low'),
)

class Subscription(models.Model):
    '''
    request_all: get all recs, from the recommender regardless of topic.
    '''
    subscriber = models.ForeignKey(User, related_name='subscriptions_in')
    recommender = models.ForeignKey(User, related_name='subscriptions_out')
    priority = models.IntegerField(choices=SUBSCRIPTION_PRIORITY_CHOICES)
    request_all = models.BooleanField()
    datetime_created = models.DateTimeField(default=datetime.now)

# see http://www.djangobook.com/en/1.0/chapter12/#cn222
class UserProfile(models.Model):
    '''In addition to these fields, there are mappings constructed
    on the User object:

    comments: comments written by this user.
    recommendations: recommendations made by this user.
    author_set: the Author object listing papers written by this user,
    if any.
    subscriptions_in: lists his subscriptions (to receive recs);
    subscriptions_out: lists his subscribers (to send recs).
    merge_requests: lists his topic merge requests.
    topicgroup_set: lists topics he created.
    submissions: paper records he created.
    '''
    user = models.ForeignKey(User, unique=True)
    datetime_joined = models.DateTimeField(default=datetime.now)
    datetime_last_seen = models.DateTimeField()
    recommenders = models.ManyToManyField(User, through='Subscription',
                                     symmetrical=False,
                                     related_name='subscribers')
    topic_groups = models.ManyToManyField(TopicGroup, related_name='members')
    
class Author(models.Model):
    '''Note that we cannot assume all paper authors will be registered
    as users of this site, so we represent authors as a separate
    table.'''
    name = models.CharField(max_length=1000)
    email =  models.CharField(max_length=1000) # is there a max length for emails?
    papers = models.ManyToManyField('Paper', related_name='authors')
    user = models.ForeignKey(User, unique=True, null=True,
                             blank=True) # is this author a user?


class PaperDB(models.Model):
    '''Represents different paper repositories, e.g. arXiv.
    Each paperdb must provide a mechanism for accessing the paper.

    url_template: should specify how to construct URL for the
    paper using paper_id and url_data.'''
    name = models.CharField(max_length=1000)
    url_template = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000)
    
    
class Paper(models.Model):
    '''mappings to other data given by the following attributes:
    authors: list of authors.
    topic_groups: list of topics assigned by submitter.
    comments: top-level comment threads for this paper.
    recommendations: recommendations of this paper.

    url_data: additional data for URL construction

    submitter: mainly informative for indicating who assigned topic_groups
    '''
    paper_db = models.ForeignKey(PaperDB, related_name='papers')
    paper_id = models.CharField(max_length=50) # for generality, make it longer
    url_data = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    topic_groups = models.ManyToManyField(TopicGroup,
                                          related_name='papers')
    submitter = models.ForeignKey(User, related_name='submissions')
    #comment_threads

class Recommendation(models.Model):
    '''recommendation object:
    Recommends a single paper to one or more topic groups;
    if no topic specified, send the rec to all subscribers of the
    recommender.
    
    Private rec. will not be displayed on the public interface;
    it will simply be used for helping to suggest other papers
    the user is likely to like.

    want_to_read just flags a paper for the users reading list;
    later s/he can decide whether or not to recommend it to others.

    review_comment attr. gives link to the text of this
    recommendation, if any.
    has_review should indicate whether such a review_comment exists.'''
    recommender = models.ForeignKey(User, related_name='recommendations')
    paper = models.ForeignKey(Paper, related_name='recommendations')
    must_read = models.BooleanField() # highest level of rec
    want_to_read = models.BooleanField() # haven't read this yet...
    private = models.BooleanField() # don't display this rec
    topic_groups = models.ManyToManyField(TopicGroup,
                                          related_name='recommendations')
    has_review = models.BooleanField()
    datetime_created = models.DateTimeField(default=datetime.now)


# Comments: http://codeblogging.net/blogs/1/3/    

class Comment(MPTTModel):
    '''threaded discussion object:
    can cite one or more papers
    can be linked to a recommendation as the text of that rec.
    can be child of a previous comment, or have any number of
    child comments.

    The actual comment can be specified in either of two ways:

    comment_text contains the actual text.

    source_url gives URL of externally published comment text,
    if any.'''
    papers = models.ManyToManyField(Paper, related_name='comments')
    title = models.CharField(max_length=1000)
    author = models.ForeignKey(User, related_name='comments')
    recommendation = models.ForeignKey(Recommendation, unique=True,
                                       null=True, blank=True,
                                       related_name='review_comment')
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')
    comment_text = models.TextField()
    source_url = models.URLField(blank=True)
    datetime_created = models.DateTimeField(default=datetime.now)

    class MPTTMeta:
        # comments on one level will be ordered by date of creation
        order_insertion_by=['datetime_created']
