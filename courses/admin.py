# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from courses.models import *

class ProfileAdmin(admin.ModelAdmin):
	pass

admin.site.register(Profile, ProfileAdmin)

class TargetAdmin(admin.ModelAdmin):
	pass

admin.site.register(Target, TargetAdmin)

# Register your models here.
#class CourseAdmin(admin.ModelAdmin):
#	pass

#admin.site.register(Course, CourseAdmin)

#class SectionAdmin(admin.ModelAdmin):
#	pass

#admin.site.register(Section, SectionAdmin)

#class QuestionAdmin(admin.ModelAdmin):
#	pass

#admin.site.register(Question, QuestionAdmin)

#class AnswerAdmin(admin.ModelAdmin):
#	pass

#admin.site.register(Answer, AnswerAdmin)