# Django
from django.shortcuts import render
from django.contrib.auth import logout
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Django REST Framework
from rest_framework import viewsets, mixins

# Scripts
from scripts.twitter import TwitterOauthClient
from scripts.facebook import *
from scripts.googlePlus import *

# Python
# from requests_oauth2 import OAuth2 as oauth
import oauth2 as oauth
import simplejson as json
import requests
import logging as LOG

# Models
from models import *
from serializers import SnippetSerializer
from forms import UserForm, HostForm, UpdateProfile, UpdateEmail, UpdatePassword

YELP_CONSUMER_KEY = '9PLzBaT21UbHC7MCS5eYkQ'
YELP_CONSUMER_SECRET = 'I9NC-0JB2Mc7H6kHD_Y-D0Lqfuk'
YELP_ACCESS_KEY = 'go7gUc6VZnAinnMRg9BB9TQ2NcUEtAEE'
YELP_ACCESS_SECRET = 'yMzMcMAiMOQyHQTWKfrqJpdQEBs'
profile_track = None


# getTwitter = TwitterOauthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
# getFacebook = FacebookOauthClient(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)
# getGoogle = GooglePlus(settings.GOOGLE_PLUS_APP_ID, settings.GOOGLE_PLUS_APP_SECRET)


##################
#   userpage     #
##################
def userpage(request, username=None):
    user = request.user
    print user.id
    location = 'Seattle, WA'
    interests = 'cars, boating, photography'
    accomodation = 'house, wifi, stuffs'
    about = 'my name is morgan freeman and you are now reading this in my voice.'
    twitter = '@ twitter username'
    facebook = 'facebook username'
    telegram = '@ telegram username'
    image = 'img/photo.jpg'

    consumer_key = YELP_CONSUMER_KEY
    consumer_secret = YELP_CONSUMER_SECRET
    access_key = YELP_ACCESS_KEY
    access_secret = YELP_ACCESS_SECRET
    site = 'https://api.yelp.com/v2/search'
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    access_token = oauth.Token(access_key, access_secret)
    client = oauth.Client(consumer, access_token)
    endpoint = 'https://api.yelp.com/v2/search/'

    # if from search engine
    if username:
        try:
            user = User.objects.get(username=username)
            uid = user.id
            host_info = HostRegistration.objects.get(user_id=uid)
            profile_info = UserProfile.objects.get(user_id=uid)
            location = "%s, %s" % (host_info.city, host_info.state)  # "new york city"
            interests = profile_info.interests  # 'sports, mountain climbing, bleh, foobar, coding'
            accomodation = profile_info.accomodation  # ['house', 'double bed', 'futon']
            about = profile_info.about
            twitter = profile_info.twitter
            facebook = profile_info.facebook
            telegram = profile_info.telegram
            image = profile_info.profile_image
            print 'fb: ', facebook
        except:
            return render(request, 'users/userpage.html')

    # if no username is specified in url, it is possible to display info just for current user
    elif not user.is_anonymous():
        print 'is anon'
        user = request.user
        username = user.username
        uid = user.id
        try:
            print 1
            host_info = HostRegistration.objects.get(user_id=uid)
            profile_info = UserProfile.objects.get(user_id=uid)
            location = "%s, %s" % (host_info.city, host_info.state)  # "new york city"
            interests = profile_info.interests  # 'sports, mountain climbing, bleh, foobar, coding'
            accomodation = profile_info.accomodation  # ['house', 'double bed', 'futon']
            about = profile_info.about
            twitter = profile_info.twitter
            facebook = str(profile_info.facebook)
            telegram = profile_info.telegram
            image = profile_info.profile_image
        except Exception as err:
            print err
    search_terms = '?term=tourist attractions&location=' + location + \
                   '&limit=10&radius_filter=10000'
    responce, data = client.request(endpoint + search_terms)
    attractions = json.loads(data)['businesses']
    listofattractions = list()
    for n in xrange(0, len(attractions)):
        listofattractions.append(attractions[n]['name'])
    context = {'username': username,
               'profile_image': image,
               'location': location,
               'yelp': listofattractions,
               'interests': interests,
               'accomodation': accomodation,
               'about': about,
               'twitter': twitter,
               'facebook': facebook,
               'telegram': telegram,
               }
    return render(request, 'users/userpage.html', context)


##################
#  edit userpage #
##################

def edit_userpage(request):
    user = request.user
    print 'outside'
    if user.is_authenticated:
        print 'is authed'
        username = user.username
        try:
            print 'try'
            profile = UserProfile.objects.get(user_id=user.id)
            print profile
            picture = profile.profile_image.url
            interests = profile.interests
            accomodation = profile.accomodation
            about = profile.about
            twitter = profile.twitter
            facebook = str(profile.facebook)
            telegram = profile.telegram
        except Exception as err:
            print err
            interests = 'interests'
            picture = 'static_dev/img/default_profile_picture.jpg'
            accomodation = 'accomodation'
            about = 'about'
            twitter = '@username'
            facebook = 'user name'
            telegram = '@username'
        if request.method == 'POST':
            print user.id
            profileID = UserProfile.objects.get(user_id=user.id)
            print profileID
            profile_form = UpdateProfile(request.POST, request.FILES, instance=profileID)
            if profile_form.is_valid():
                instance = profile_form.save(commit=False)
                print 'instance %s' % profile_form
                print 'FILES: ', request.FILES
                if 'image' in request.FILES:
                    instance.profile_image = request.FILES['image']
                instance.save()
                return HttpResponseRedirect('/userpage/')
            else:
                print profile_form.errors

        context = {'username': username,
                   'picture': picture,
                   'interests': interests,
                   'accomodation': accomodation,
                   'about': about,
                   'twitter': twitter,
                   'facebok': str(facebook),
                   'telegram': telegram,
                   }
        return render(request, 'users/edit_userpage.html', context)
    else:
        return HttpResponseRedirect('/')


##################
#   dashboard    #
# currently inop #
##################

def user_dashboard(request, username=None):
    user = request.user
    if username:
        try:
            user = User.objects.get(username=username)
        except:
            return render(request, 'users/dashboard.html')
    # if no username is specified in url, it is possible to display info just for current user
    elif not user.is_anonymous():
        user = request.user
    else:
        return render(request, 'users/dashboard.html')
    username = user.username
    schedule = "here be dragons between january and december"
    messages = "To from and inbetween"

    # for pictures: http://ashleydw.github.io/lightbox/
    context = {'username': username,
               'schedule': schedule,
               'messages': messages,
               }
    return render(request, 'users/dashboard.html', context)


#########################
#     User Settings     #
#########################

def user_settings(request):
    user = request.user
    if request.method == 'POST' and 'user_delete' in request.POST:
        try:
            u = user
            u.delete()
            logout(request)
            return render(request, 'users/login.html')
        except User.DoesNotExist:
            return render(request, 'users/login.html')
        except Exception as e:
            return render(request, 'users/login.html', {'err': e.message})
    elif request.method == 'POST' and 'user_update_email' in request.POST:
        u = user
        update_email = UpdateEmail(data=request.POST, instance=u)
        if update_email.is_valid():
            update_email.save()
            return render(request, 'users/user_settings.html')
    elif request.method == "POST" and "user_update_password" in request.POST:
        u = user
        username = request.POST.get(user)
        password = request.POST.get('current_password')
        # user = authenticate(username=username, password=password)
        # if user:
        update_password = UpdatePassword(data=request.POST, instance=u)
        if update_password.is_valid():
            user = update_password.save()
            user.set_password(user.password)
            user.save()
            return render(request, 'users/user_settings.html')
            # else:
            #     return render(request, 'users/userpage.html')

    else:
        return render(request, 'users/user_settings.html')

    return render(request, 'users/user_settings.html')


#########################
# Snippet RESTful Model #
#########################

class CRUDBaseView(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    pass


class SnippetView(CRUDBaseView):
    serializer_class = SnippetSerializer
    queryset = Snippet.objects.all()


######################
# Registration Views #
######################
# normal user
def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
        else:
            print user_form.errors
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user.is_authenticated:
            login(request, user)
            profile = UserProfile(user_id=user.id)
            profile.save()
            return HttpResponseRedirect('../chooser')
        else:
            raise Exception("user is not authenticated")
    else:
        user_form = UserForm()
    return render(request,
                  'users/register.html',
                  {'user_form': user_form, 'registered': registered})


# become a host
def host_register(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'POST':
            host_form = HostForm(data=request.POST)
            if host_form.is_valid():
                instance = host_form.save(commit=False)
                instance.user = request.user
                instance.save()
                return HttpResponseRedirect('/edit_userpage/')
            else:
                print host_form.errors
    else:
        return HttpResponseRedirect('/')
    guide_form = HostForm()
    context = {'guide_form': guide_form}
    return render(request, 'users/host.html', context)


######################
#       chooser      #
######################
def chooser(request):
    user = request.user
    if user:
        print 'foo'
    if request.POST.get('yes_btn'):
        return HttpResponseRedirect('/host/')
    elif request.POST.get('no_btn'):
        return HttpResponseRedirect('/edit_userpage/')
    context = {'user': user}
    return render(request, 'users/chooser.html', context)


######################
#       Login        #
######################
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your Django Hackathon account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'users/login.html', {})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')
