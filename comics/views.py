from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, renderers
from rest_framework.decorators import api_view, detail_route
from .models import Series, Issue, Character, Arc, Team, Publisher, Creator, Settings, Roles
from .serializers import ArcSerializer, CharacterSerializer, CreatorSerializer, \
	GroupSerializer, IssueSerializer, PublisherSerializer, SeriesSerializer, \
	SettingsSerializer, TeamSerializer, UserSerializer

def index(request):
	return render(request, 'comics/index.html')

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
