# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework import viewsets

from students.models import *
from courses.models import *
from api.serializers import *

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.order_by('-date_joined')
	serializer_class = UserSerializer