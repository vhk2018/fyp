from rest_framework import serializers

from students.models import User
from courses.models import *

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['username','email',]
		
class SectionSerializer(serializers.ModelSerializer):
    #modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['number', ]