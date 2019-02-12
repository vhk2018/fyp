from django import forms

from courses.models import *

class CourseForm(forms.ModelForm):
	
	class Meta:
		model = CoursePage
		fields = ['name', ]