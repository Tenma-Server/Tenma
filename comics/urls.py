from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'comics'
urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^series/(?P<pk>[0-9]+)$', views.SeriesView.as_view(), name='series'),
	url(r'^issue/(?P<pk>[0-9]+)$', views.IssueView.as_view(), name='issue'),
	url(r'^issue/(?P<issue_id>[0-9]+)/read$', views.read, name='read'),
	url(r'^character/(?P<pk>[0-9]+)$', views.CharacterView.as_view(), name='character'),
	url(r'^arc/(?P<pk>[0-9]+)$', views.ArcView.as_view(), name='arc'),
	url(r'^team/(?P<pk>[0-9]+)$', views.TeamView.as_view(), name='team'),
	url(r'^publisher/(?P<pk>[0-9]+)$', views.PublisherView.as_view(), name='publisher'),
	url(r'^creator/(?P<pk>[0-9]+)$', views.CreatorView.as_view(), name='creator'),
	url('testing_cvscraper', views.cvscraper, name='cvscraper'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)