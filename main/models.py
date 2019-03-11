# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime

from django.core.urlresolvers import reverse
from django.conf import settings

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

from students.models import User

# Create your models here.
class Questions(models.Model):
    question_id = models.AutoField(primary_key=True)
    question = models.TextField()

    def __str__(self):
        return (self.question)

    class Meta:
        verbose_name_plural="Questions"

class Essays(models.Model):
    essay_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Questions,on_delete=models.CASCADE)
    essay_content = models.TextField()
    groundtruth_score = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    predicted_score = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    submited_at = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return (self.essay_content)

    class Meta:
        verbose_name_plural= "Essays"

		# Create your models here.

class EssayIndexPage(Page):
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [FieldPanel('intro', classname="full")]

    #def get_context(self, request):
		#context = super(CourseIndexPage, self).get_context(request)
		#coursepages = self.get_children().live().order_by('-first_published_at')
		#context['coursepages'] = coursepages
		#return context
		