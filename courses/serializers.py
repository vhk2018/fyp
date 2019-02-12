from rest_framework import serializers

from courses.models import *

class CourseSerializer(serializers.ModelSerializer):
    #modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
		#fields = ('id', 'subject', 'title', 'slug', 'overview', 'created', 'overview', 'created', 'owner', 'modules', )
		
class SectionSerializer(serializers.ModelSerializer):
    #modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ('number', )