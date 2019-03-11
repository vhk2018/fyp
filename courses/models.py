# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

from students.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect
import json
from django.http import HttpResponse

# Create your models here.
class CourseIndexPage(Page):
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [FieldPanel('intro', classname="full")]

    def get_context(self, request):
		context = super(CourseIndexPage, self).get_context(request)
		coursepages = self.get_children().live().order_by('-first_published_at')
		context['coursepages'] = coursepages
		return context
		
    def serve(self, request):
        if request.method=='POST':
			data = request.POST.get('coursename')
			print data
			if data:
				return HttpResponse(json.dumps({'message': 'added'}), content_type="application/json")
			return JsonResponse({'message': 'failed'})#HttpResponse(json.dumps({'message': 'failed'}), content_type="application/json")
        context = super(CourseIndexPage, self).get_context(request)
        coursepages = self.get_children().live().order_by('-first_published_at')
        context['coursepages'] = coursepages
		#return context
        return render(request, 'courses/course_index_page.html', context)
		

class Course(models.Model):
	
	
	def get_absolute_url(self):
		return reverse('course_detail', args=(self.id, ))
		
	def __str__ (self):
		return self.name

class CoursePageTag(TaggedItemBase):
	content_object = ParentalKey('CoursePage', related_name = 'tagged_items', null=True)
	def get_context(self, request):
	
		#filter by tag
		tag = request.GET.get('tag')
		coursepages = CoursePage.objects.filter(tags__name=tag)
		
		#update template context
		context = super(CourseTagIndexPage, self).get_context(request)
		context['coursepages']=coursepages
		return context
		
class CoursePage(Page):

	#database fields
	date = models.DateField("Post Date")
	name = models.CharField(max_length=200)
	intro = models.CharField(max_length=250)
	students = models.ManyToManyField(User)
	body = RichTextField(blank=True)
	feed_image = models.ForeignKey(
		'wagtailimages.Image',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)
	
	tags = ClusterTaggableManager(through=CoursePageTag, blank = True)
    #body = RichTextField(blank=True)
	
	# search index configuration
	
	search_fields = Page.search_fields + [
        index.SearchField('name'),
		index.SearchField('intro'),
		index.SearchField('body'),
		index.FilterField('date'),
    ]
	
	# editor panels configuration
	
	content_panels = Page.content_panels + [	
		MultiFieldPanel([
			FieldPanel('date'),
			FieldPanel('tags'),		
		], heading = 'Course information'),
					
        FieldPanel('name'),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
        InlinePanel('gallery_images', label="Gallery images"),
		InlinePanel('related_links', label="Related links"),
    ]
	
	promote_panels = [
		MultiFieldPanel(Page.promote_panels, "Common page configuration"),
		ImageChooserPanel('feed_image'),
	]
	
	# parent page/subpage type rules
	
	parent_page_types = ['courses.CourseIndexPage']
	subpage_types = ['courses.SectionPage']
	
	def get_absolute_url(self):
		return reverse('course_detail', args=(self.id, ))
		
	def __str__ (self):
		return self.name
	
	def main_image(self):
		gallery_item = self.gallery_images.first()
		if gallery_item:
			return gallery_item.image
		else:
			return None
		
	def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron = .order_by('-first_published_at')
		context = super(CoursePage, self).get_context(request)
		sections = self.get_children().live().order_by('first_published_at')
		context['sections'] = sections
		units = []
		#print sections
		for s in sections:
			units.append(s.specific.number)
		units = list(set(units))
		context['units']=units
		return context

	
class CoursePageGalleryImage(Orderable):
    page = ParentalKey(CoursePage, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]

class CoursePageRelatedLink(Orderable):
	page = ParentalKey(CoursePage, related_name='related_links')
	name = models.CharField(max_length=255)
	url = models.URLField()
	
	panels = [
		FieldPanel('name'),
		FieldPanel('url'),
	]
#class Section		
class Section(models.Model):
	course = models.ForeignKey(Course)
	name = models.CharField(max_length=300)
	number = models.IntegerField() #the order of section in the course
	text = models.TextField() #the section content
	
	class Meta:
		unique_together = ('course','number',)
	
	def __str__(self):
		return self.name
		
	def get_test_url(self):
		return reverse('do_test', args=(self.id,))
		
	def get_absolute_url(self):
		return reverse('do_section', args=(self.id,))
		
	def get_next_section_url(self):
		next_section = Section.objects.get(number=self.number+1)
		return reverse('do_section', args=(next_section.id,))
	

class SectionPage(Page):

	#database fields
	#date = models.DateField("Post Date")
	#course = models.ForeignKey(CoursePage)
	name = models.CharField(max_length=300)
	number = models.IntegerField() #the order of section in the course
	text = models.TextField() #the section content
	#body = RichTextField(blank=True)
	feed_image = models.ForeignKey(
		'wagtailimages.Image',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)
	
	search_fields = Page.search_fields + [
        #index.SearchField('course'),
		index.SearchField('name'),
		index.SearchField('text'),
		#index.FilterField('date'),
    ]
	
	# editor panels configuration
	
	content_panels = Page.content_panels + [	
		#MultiFieldPanel([
		#	FieldPanel('date'),
			#FieldPanel('tags'),		
		#], heading = 'Section information'),
					
        #FieldPanel('course'),
        FieldPanel('name'),
		FieldPanel('number'),
        FieldPanel('text', classname="full"),
        InlinePanel('section_images', label="Section images"),
		#InlinePanel('related_links', label="Related links"),
    ]
	
	promote_panels = [
		MultiFieldPanel(Page.promote_panels, "Common page configuration"),
		ImageChooserPanel('feed_image'),
	]
	
	# parent page/subpage type rules
	
	parent_page_types = ['courses.CoursePage']
	subpage_types = ['courses.QuestionPage']	
	
class SectionPageGalleryImage(Orderable):
    page = ParentalKey(SectionPage, related_name='section_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]
	
class Question(models.Model):
	section = models.ForeignKey(Section)
	text = models.CharField(max_length=1000)
	
	def __str__(self):
		return self.text

class QuestionPage(Page):

	#database fields
	#date = models.DateField("Post Date")
	section = models.ForeignKey(SectionPage)
	text = models.CharField(max_length=1000)
	feed_image = models.ForeignKey(
		'wagtailimages.Image',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)
	
	search_fields = Page.search_fields + [
        index.SearchField('section'),
		index.SearchField('text'),
		#index.FilterField('date'),
    ]
	
	# editor panels configuration
	
	content_panels = Page.content_panels + [	
		#MultiFieldPanel([
		#	FieldPanel('date'),
			#FieldPanel('tags'),		
		#], heading = 'Question information'),
					
        FieldPanel('section'),
        FieldPanel('text', classname="full"),
        InlinePanel('question_images', label="Question images"),
		#InlinePanel('related_links', label="Related links"),
    ]
	
	promote_panels = [
		MultiFieldPanel(Page.promote_panels, "Common page configuration"),
		ImageChooserPanel('feed_image'),
	]
	
	# parent page/subpage type rules
	
	parent_page_types = ['courses.SectionPage']
	subpage_types = ['courses.AnswerPage']	
	
	def __str__(self):
		return self.text
	
class QuestionPageGalleryImage(Orderable):
    page = ParentalKey(QuestionPage, related_name='question_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]
	
		
class Answer(models.Model):
	date = models.DateField("Post Date")
	question = models.ForeignKey(Question)
	text = models.CharField(max_length=1000)
	correct = models.BooleanField()
	
	def __str__(self):
		return self.text

class AnswerPage(Page):

	#database fields
	#date = models.DateField("Post Date")
	question = models.ForeignKey(Question)
	text = models.CharField(max_length=1000)
	correct = models.BooleanField()
	
	search_fields = Page.search_fields + [
        index.SearchField('question'),
		index.SearchField('text'),
		#index.FilterField('date'),
    ]
	
	# editor panels configuration
	
	content_panels = Page.content_panels + [	
		#MultiFieldPanel([
		#	FieldPanel('date'),
		#	#FieldPanel('tags'),		
		#], heading = 'Answer information'),
					
        FieldPanel('question'),
        FieldPanel('text', classname="full"),
        #InlinePanel('question_images', label="Question images"),
		#InlinePanel('related_links', label="Related links"),
    ]
	
	promote_panels = [
		MultiFieldPanel(Page.promote_panels, "Common page configuration"),
		#ImageChooserPanel('feed_image'),
	]
	
	# parent page/subpage type rules
	
	parent_page_types = ['courses.QuestionPage']
	subpage_types = ['courses.UserAnswerPage']	
	
	def __str__(self):
		return self.text
		
class UserAnswer(models.Model):
	question = models.ForeignKey(Question)
	answer = models.ForeignKey(Answer)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	
	class Meta:
		unique_together = ('question', 'user',)
		
class UserAnswerPage(Page):

	#database fields
	date = models.DateField("Post Date")
	question = models.ForeignKey(Question)
	answer = models.ForeignKey(Answer)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	
	search_fields = Page.search_fields + [
        index.SearchField('question'),
		index.SearchField('answer'),
		index.SearchField('user'),
		index.FilterField('date'),
    ]
	
	# editor panels configuration
	
	content_panels = Page.content_panels + [	
		MultiFieldPanel([
			FieldPanel('date'),
			#FieldPanel('tags'),		
		], heading = 'UserAnswer information'),
					
        FieldPanel('question'),
        FieldPanel('answer', classname="full"),
		FieldPanel('user'),
        #InlinePanel('question_images', label="Question images"),
		#InlinePanel('related_links', label="Related links"),
    ]
	
	promote_panels = [
		MultiFieldPanel(Page.promote_panels, "Common page configuration"),
		#ImageChooserPanel('feed_image'),
	]
	
	# parent page/subpage type rules
	
	parent_page_types = ['courses.AnswerPage']
	subpage_types = []	
	
	class Meta:
		unique_together = ('question', 'user',)
		
class Profile(models.Model):
    ''' This defines the Profile model, which represents a user's profile.
            user is the Django User model which has one-to-one relationship with the profile.
            subjects defines the Subject models which have a many-to-many relationship with the profile and represents
            the subjects taken by this user. Each relationship is extended by a Grade model.
            interests defines the Interest models which have a many-to-many relationship with the profile and represents
            the subject interest areas of the user.
            targets defines the Course models which have a many-to-many relationship with the profile and represents
            the target courses of the user. Each relationship is extended by a Target model.
            l1r4_X is an integer defining the calculated L1R4 score of the user, where X is the L1R4 group and ranges from
            A, B, C, to D. '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course = models.ManyToManyField(CoursePage, through='Target')
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    ''' This function creates new Profile model instance each time a new User model instance is created and
            links the two models together under a one-to-one relationship. '''
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    ''' This function saves the Profile model instance linked to the User model instance whenever the latter
            is saved. '''
    instance.profile.save()
	
class Target(models.Model):
    ''' This defines the Target model, which represents the target course of a user. It is created for each
            many-to-many relationship between a Profile model and Course Page model.
            profile defines the foreign key to the Profile model.
            course defines the foreign key to the Course Page model.
            rank is an integer defining the rank selected by the user for this target course. '''
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    course = models.ForeignKey(CoursePage, on_delete=models.CASCADE)
    #rank = models.IntegerField()         
    def __str__ (self):
		return self.profile.user.username + self.course.name