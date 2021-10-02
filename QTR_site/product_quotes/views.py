from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from dictionary.models import Entry
from dictionary.utils import * #to get random entries, quizes
from userinfo.utils import * #to get user profile and stats
from django.template import loader
from django.http import Http404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from random import *
from django.core.mail import send_mail

#def create_quote(request):
#def create_license(request):
