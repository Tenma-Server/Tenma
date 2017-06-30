from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, renderers
from rest_framework.decorators import api_view, detail_route
from .models import Series, Issue, Character, Arc, Team, Publisher, Creator, Settings
from .serializers import ArcSerializer, CharacterSerializer, CreatorSerializer, \
	GroupSerializer, IssueSerializer, PublisherSerializer, SeriesSerializer, \
	SettingsSerializer, TeamSerializer, UserSerializer
from .tasks import import_comic_files_task, reprocess_issue_task

class IndexView(ListView):
	template_name = 'comics/index.html'
	context_object_name = 'all_series'

	def get_queryset(self):
		return Series.objects.order_by('name')

class SeriesView(DetailView):
	model = Series
	template_name = 'comics/series.html'

class IssueView(DetailView):
	model = Issue
	template_name = 'comics/issue.html'

class CharacterView(DetailView):
	model = Character
	template_name = 'comics/character.html'

	def get_context_data(self, **kwargs):
		context = super(CharacterView, self).get_context_data(**kwargs)
		character = self.get_object()
		context['issue_list'] = character.issue_set.all().order_by('series__name', 'number')
		return context

class ArcView(DetailView):
	model = Arc
	template_name = 'comics/arc.html'

	def get_context_data(self, **kwargs):
		context = super(ArcView, self).get_context_data(**kwargs)
		arc = self.get_object()
		context['issue_list'] = arc.issue_set.all().order_by('series__name', 'number')
		return context

class TeamView(DetailView):
	model = Team
	template_name = 'comics/team.html'

	def get_context_data(self, **kwargs):
		context = super(TeamView, self).get_context_data(**kwargs)
		team = self.get_object()
		context['issue_list'] = team.issue_set.all().order_by('series__name', 'number')
		return context

class PublisherView(DetailView):
	model = Publisher
	template_name = 'comics/publisher.html'

class CreatorView(DetailView):
	model = Creator
	template_name = 'comics/creator.html'

	def get_context_data(self, **kwargs):
		context = super(CreatorView, self).get_context_data(**kwargs)
		creator = self.get_object()
		context['issue_list'] = creator.issue_set.all().order_by('series__name', 'number')
		return context

class ServerSettingsView(UpdateView):
	model = Settings
	fields = '__all__'
	template_name = 'comics/server_settings.html'

	def get_object(self, *args, **kwargs):
		return Settings.get_solo()

	def form_valid(self, form):
		self.object = form.save()
		return render(self.request, 'comics/server-settings-success.html', {'server-settings': self.object})

class IssueUpdateView(UpdateView):
	model = Issue
	fields = ['cvid']
	template_name = 'comics/issue_update.html'

	def form_valid(self, form):
		self.object = form.save()
		return render(self.request, 'comics/issue_update_success.html', {'issue-update': self.object})

def read(request, issue_id):
	issue = get_object_or_404(Issue, pk=issue_id)
	return render(request, 'comics/read.html', {'issue': issue})

def importer(request):
	import_comic_files_task.delay()
	return HttpResponseRedirect('/')

def reprocess(request, issue_id):
	reprocess_issue_task.delay(issue_id)
	return HttpResponseRedirect('/issue/' + issue_id)

# API VIEWS #

@api_view(['GET'])
def api_root(request, format=None):
	return Response({
		'arcs': reverse('arc-list', request=request, format=format),
		'characters': reverse('character-list', request=request, format=format),
		'creators': reverse('creator-list', request=request, format=format),
		'groups': reverse('group-list', request=request, format=format),
		'issues': reverse('issue-list', request=request, format=format),
		'publishers': reverse('publisher-list', request=request, format=format),
		'series': reverse('series-list', request=request, format=format),
		'settings': reverse('settings-list', request=request, format=format),
		'teams': reverse('team-list', request=request, format=format),
		'users': reverse('user-list', request=request, format=format),
	})

class ArcViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows arcs to be viewed or edited.
	"""
	queryset = Arc.objects.all()
	serializer_class = ArcSerializer

	@detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
	def issues(self, request, *args, **kwargs):
		arc = self.get_object()
		return Response(arc.issues)

class CharacterViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows characters to be viewed or edited.
	"""
	queryset = Character.objects.all()
	serializer_class = CharacterSerializer

	@detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
	def issues(self, request, *args, **kwargs):
		character = self.get_object()
		return Response(character.issues)

	@detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
	def teams(self, request, *args, **kwargs):
		character = self.get_object()
		return Response(character.teams)

class CreatorViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows creators to be viewed or edited.
	"""
	queryset = Creator.objects.all()
	serializer_class = CreatorSerializer

	@detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
	def issues(self, request, *args, **kwargs):
		creator = self.get_object()
		return Response(creator.issues)

class GroupViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows groups to be viewed or edited.
	"""
	queryset = Group.objects.all()
	serializer_class = GroupSerializer

class IssueViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows issues to be viewed or edited.
	"""
	queryset = Issue.objects.all()
	serializer_class = IssueSerializer

	@detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
	def arcs(self, request, *args, **kwargs):
		issue = self.get_object()
		return Response(issues.arcs)

	@detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
	def characters(self, request, *args, **kwargs):
		issue = self.get_object()
		return Response(issues.characters)

	@detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
	def creators(self, request, *args, **kwargs):
		issue = self.get_object()
		return Response(issues.creators)

	@detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
	def teams(self, request, *args, **kwargs):
		issue = self.get_object()
		return Response(issues.teams)

class PublisherViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows publishers to be viewed or edited.
	"""
	queryset = Publisher.objects.all()
	serializer_class = PublisherSerializer

	@detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
	def series(self, request, *args, **kwargs):
		publisher = self.get_object()
		return Response(publisher.series)

class SeriesViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows series to be viewed or edited.
	"""
	queryset = Series.objects.all()
	serializer_class = SeriesSerializer

class SettingsViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows server settings to be viewed or edited.
	"""
	queryset = Settings.objects.all()
	serializer_class = SettingsSerializer

class TeamViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows teams to be viewed or edited.
	"""
	queryset = Team.objects.all()
	serializer_class = TeamSerializer

	@detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
	def issues(self, request, *args, **kwargs):
		team = self.get_object()
		return Response(team.issues)

class UserViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows users to be viewed or edited.
	"""
	queryset = User.objects.all().order_by('-date_joined')
	serializer_class = UserSerializer
