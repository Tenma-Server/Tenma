"""tenma URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from comics import views
from rest_framework import routers
from rest_framework.schemas import get_schema_view

router = routers.DefaultRouter()
router.register(r'arcs', views.ArcViewSet)
router.register(r'characters', views.CharacterViewSet)
router.register(r'creators', views.CreatorViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'issues', views.IssueViewSet)
router.register(r'publishers', views.PublisherViewSet)
router.register(r'series', views.SeriesViewSet)
router.register(r'settings', views.SettingsViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'users', views.UserViewSet)

schema_view = get_schema_view(title='Tenma API')

urlpatterns = [
	url('^v1/schema/$', schema_view),
	url(r'', include('comics.urls')),
	url(r'^v1/', include(router.urls)),
	url(r'^admin/', admin.site.urls),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
