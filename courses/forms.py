from django import forms

from courses.models import *
from django.contrib.auth.forms import UserCreationForm
from students.models import User

class CourseForm(forms.ModelForm):
	
	class Meta:
		model = CoursePage
		fields = ['name', ]
		
class SignUpForm(UserCreationForm):
    ''' This defines the form used to receive user input to create an account and fill in details. 
            The form saves the data into the Django User model.
            username is a field defining the username of the user and is the primary key of the User model.
            first_name is a field defining the first name of the user.
            email is a field defining the email of the user.
            password1 and password2 are fields defining the password of the user. Both fields need to match. '''
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')