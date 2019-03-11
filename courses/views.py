# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import logout, login, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db import transaction
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.urlresolvers import reverse

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from courses.forms import CourseForm, SignUpForm
from courses.models import *
from courses.serializers import SectionSerializer

import json
from django.http import JsonResponse

# Create your views here.
def course_detail(request, course_id):
	course = Course.objects.get(id=course_id)
	return render(request, 'courses/course_detail.html', {
		'course':course,
	})

def course_list(request):
	courses = Course.objects.prefetch_related('students') #Course.objects.all()
	return render(request, 'courses/course_list.html', {
		'courses': courses,
	})
	
def course_add(request):
	if request.POST:
		form = CourseForm(request.POST)
		if form.is_valid():
			new_course = form.save()
			return HttpResponseRedirect(new_course.get_absolute_url())
	else:
		form = CourseForm()
	return render(request, 'courses/course_form.html', {
		'form': form,
	})
	
def do_section(request, section_id):
	section = Section.objects.get(id=section.id)
	return render(request, 'courses/do_section.html', {
		'section':section,
	})

def do_test(request, section_id):
	if not request.user.is_authenticated():
		raise PermissionDenied
	section = Section.objects.get(id=section_id)
	if request.method == 'POST':
		data = {}
		#with transaction.atomic():
			#UserAnswer.objects.filter(user=request.user,question__section=section).delete()
			
		for key, value in request.POST.items():
			if key == 'csrfmiddlewaretoken':
				continue
				# {'question-1':'2'}
				question_id=key.split('-')[1]
				question = Question.objects.get(id=question_id)
				answer_id = int(request.POST.get(key))
				#if answer_id not in question.answer_set.values_list('id', flat=True):
				#	raise SuspiciousOperation('Answer is not valid for this question')
				#user_answer = UserAnswer.objects.create(
				#	user=request.user,
				#	question=question,
				#	answer_id=answer_id,
				#)
			perform_test(request.user, data, section)
			return redirect(reverse('show_results', args=(section.id,)))
		return render(request,'courses/do_test.html',{
			'section':section,
		})
		
def perform_test(user, data, section):
	with transaction.atomic():
		UserAnswer.objects.filter(user=user, question__section=section).delete()
		for question_id, answer_id in data.items():
			question = Question.objects.get(id=question_id)
			answer_id = int(answer_id)
			if answer_id not in question.answer_set.values_list('id', flat=True):
				raise SuspiciousOperation('Answer is not valid for this quesiton')
			user_answer = UserAnswer.objects.create(
				user=request.user,
				question=question,
				answer_id=answer_id,
			)
		
def calculate_score(user, section):
	questions = Question.objects.filter(section=section)
	correct_answer = UserAnswer.objects.filter(
		user=user,
		question__section=section,
		answer__correct=True
	)
	return (correct_answer.count() / questions.count()) * 100

def show_results(request, section_id):
	if not request.user.is_authenticated():
		raise PermissionDenied
	section = Section.objects.get(id=section_id)
	return render(request, 'courses/show_results.html', {
		'section': section,
		'score': calculate_score(request.user, section),
	})
	
class SectionViewSet(viewsets.ModelViewSet):
	queryset = Section.objects.all()
	serializer_class = SectionSerializer
	
	@detail_route(method=['GET', ])
	def questions(self, request, *args, **kwargs):
		section = self.get_object()
		data = []
		for question in section.question_set.all():
			question_data = {'id':question.id, 'answers': []}
			for answer in question.answer_set.all():
				answer_data = {'id':answer.id, 'text':str(answer), }
				question_data['answer'].append(answer_data)
			data.append(question_data)
		return Response(data)
		
def signup(request):
    ''' This function renders the html page to allow a user to sign up and create a new account by rendering a
            SignUpForm form.
            After checking that the form is valid, the data retrieved from the form is used to create
            a new User model instance. '''
    if request.method=='POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
            form = SignUpForm()
    return render(request, 'courses/signup.html',{'form': form})
	
def addCourse(request):
    ''' This function renders the html page to allow the user to add a new target course to their profile by
            rendering a BaseTargetFormSet formset.
            After checking that the form is valid, the data retrieved is used to create new Target model instances,
            which are linked to the Profile of the user. '''
	
    data = request.POST.get('coursename')
    print data
    if data:
		return HttpResponse(json.dumps({'message': 'added'}), content_type="application/json")
    return JsonResponse({'message': 'failed'})#HttpResponse(json.dumps({'message': 'failed'}), content_type="application/json")
	
def contact(request):
    ''' This function renders the html page to contact form '''
    
    return render(request, 'courses/contact.html',{})