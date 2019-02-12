# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from students.models import User

# Register your models here.
class UserAdmin(BaseUserAdmin):
	pass

admin.site.register(User, UserAdmin)
