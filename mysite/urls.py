from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static

from rest_framework import routers

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls

from search import views as search_views
from courses.views import *
from students.views import *
from api.views import *

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls)),
	#url(r'^essay/$',include('main.urls')),
    url(r'^essay/',include('main.urls')),
    #url(r'^admin/', admin.site.urls),
	
	url(r'^', include('django.contrib.auth.urls', namespace='auth')),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^search/$', search_views.search, name='search'),
	
	url(r'^courses/$', course_list, name='course_list'),
	url(r'^course_detail/(?P<course_id>\d+)/$', course_detail, name='course_detail'),
	url(r'^course_add/$', course_add, name='course_add'),
	
	url(r'^section/(?P<section_id>\d+)/$', do_section, name='do_section'),
	url(r'^section/(?P<section_id>\d+)/test/$', do_test, name='do_test'),
	url(r'^section/(?P<section_id>\d+)/results/$', show_results, name='show_results'),
	
	url(r'^student_detail/$', student_detail, name='student_detail'),
	
	url(r'^api/', include(router.urls)),
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    url(r'', include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    url(r'^pages/', include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
