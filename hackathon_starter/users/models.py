from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username


class Profile(models.Model):
    user = models.ForeignKey(User)
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.user)


# class TwitterProfile(models.Model):
#     user = models.ForeignKey(User)
#     twitter_user = models.CharField(max_length=200)
#     oauth_token = models.CharField(max_length=200)
#     oauth_token_secret = models.CharField(max_length=200)

#     def __unicode__(self):
#         return unicode(self.user)


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)

    class Meta:
        ordering = ('created',)


# class HostForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput())
#     # address = forms.CharField()
#     # city = forms.CharField()
#     # country = forms.CharField()
#     class Meta:
#         model = Host
#         fields = ['username', 'email', 'password', 'address', 'city', 'country']


# class FacebookProfile(models.Model):
#     user = models.ForeignKey(User)
#     fb_user_id = models.CharField(max_length=100)
#     time_created = models.DateTimeField(auto_now_add=True)
#     profile_url = models.CharField(max_length=50)
#     access_token = models.CharField(max_length=100)


# class GoogleProfile(models.Model):
#     user = models.ForeignKey(User)
#     google_user_id = models.CharField(max_length=100)
#     time_created = models.DateTimeField(auto_now_add=True)
#     access_token = models.CharField(max_length=100)
#     profile_url = models.CharField(max_length=100)