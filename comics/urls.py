from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from comics.views import IndexView, SeriesView, IssueView, CharacterView, ArcView, \
						 TeamView, PublisherView, CreatorView, IssueUpdateView, ServerSettingsView, \
						 read, importer, reprocess

from . import views

app_name = 'comics'
urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^series/(?P<pk>[0-9]+)$', SeriesView.as_view(), name='series'),
	url(r'^issue/(?P<pk>[0-9]+)$', IssueView.as_view(), name='issue'),
	url(r'^issue/(?P<issue_id>[0-9]+)/read$', read, name='read'),
	url(r'^character/(?P<pk>[0-9]+)$', CharacterView.as_view(), name='character'),
	url(r'^arc/(?P<pk>[0-9]+)$', ArcView.as_view(), name='arc'),
	url(r'^team/(?P<pk>[0-9]+)$', TeamView.as_view(), name='team'),
	url(r'^publisher/(?P<pk>[0-9]+)$', PublisherView.as_view(), name='publisher'),
	url(r'^creator/(?P<pk>[0-9]+)$', CreatorView.as_view(), name='creator'),
	url('importer', importer, name='importer'),
	url(r'^issue/(?P<pk>[0-9]+)/update/$', IssueUpdateView.as_view(), name='issue-update'),
	url(r'^issue/(?P<issue_id>[0-9]+)/reprocess$', reprocess, name='reprocess'),
	url(r'^server-settings', ServerSettingsView.as_view(), name='server-settings'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)