# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

# Create your models here.
class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [FieldPanel('intro', classname="full")]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(BlogIndexPage, self).get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context
    
class BlogPageTag(TaggedItemBase):
	content_object = ParentalKey('BlogPage', related_name = 'tagged_items', null=True)
	def get_context(self, request):
	
		#filter by tag
		tag = request.GET.get('tag')
		blogpages = BlogPage.objects.filter(tags__name=tag)
		
		#update template context
		context = super(BlogTagIndexPage, self).get_context(request)
		context['blogpages']=blogpages
		return context
	
class BlogPage(Page):

	#database fields
	date = models.DateField("Post Date")
	body = RichTextField(blank=True)
	date = models.DateField("Post date")
	feed_image = models.ForeignKey(
		'wagtailimages.Image',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)
	intro = models.CharField(max_length=250)
	tags = ClusterTaggableManager(through=BlogPageTag, blank = True)
    #body = RichTextField(blank=True)
	
	# search index configuration
	
	search_fields = Page.search_fields + [
		index.SearchField('intro'),
		index.SearchField('body'),
		index.FilterField('date'),
    ]
	
	# editor panels configuration
	
	content_panels = Page.content_panels + [	
		MultiFieldPanel([
			FieldPanel('date'),
			FieldPanel('tags'),		
		], heading = 'Blog information'),
					
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
	
	parent_page_types = ['blog.BlogIndexPage']
	subpage_types = []
	
class BlogPageRelatedLink(Orderable):
	page = ParentalKey(BlogPage, related_name='related_links')
	name = models.CharField(max_length=255)
	url = models.URLField()
	
	panels = [
		FieldPanel('name'),
		FieldPanel('url'),
	]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]