from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.http import HttpResponseRedirect

from .models import Series, Issue, Character, Arc, Team, Publisher, Creator
from .utils.cvscraper import CVScraper

class IndexView(generic.ListView):
	template_name = 'comics/index.html'
	context_object_name = 'all_series'

	def get_queryset(self):
		return Series.objects.order_by('name')

class SeriesView(generic.DetailView):
	model = Series
	template_name = 'comics/series.html'

class IssueView(generic.DetailView):
	model = Issue
	template_name = 'comics/issue.html'
	
class CharacterView(generic.DetailView):
	model = Character
	template_name = 'comics/character.html'

	def get_context_data(self, **kwargs):
		context = super(CharacterView, self).get_context_data(**kwargs)
		character = self.get_object()
		context['issue_list'] = character.issue_set.all().order_by('series__name', 'number')
		return context

class ArcView(generic.DetailView):
	model = Arc
	template_name = 'comics/arc.html'

	def get_context_data(self, **kwargs):
		context = super(ArcView, self).get_context_data(**kwargs)
		arc = self.get_object()
		context['issue_list'] = arc.issue_set.all().order_by('series__name', 'number')
		return context

class TeamView(generic.DetailView):
	model = Team
	template_name = 'comics/team.html'

	def get_context_data(self, **kwargs):
		context = super(TeamView, self).get_context_data(**kwargs)
		team = self.get_object()
		context['issue_list'] = team.issue_set.all().order_by('series__name', 'number')
		return context

class PublisherView(generic.DetailView):
	model = Publisher
	template_name = 'comics/publisher.html'

class CreatorView(generic.DetailView):
	model = Creator
	template_name = 'comics/creator.html'

	def get_context_data(self, **kwargs):
		context = super(CreatorView, self).get_context_data(**kwargs)
		creator = self.get_object()
		context['issue_list'] = creator.issue_set.all().order_by('series__name', 'number')
		return context

def read(request, issue_id):
	issue = get_object_or_404(Issue, pk=issue_id)
	return render(request, 'comics/read.html', {'issue': issue})

def importer(request):
	cvscraper = CVScraper()
	cvscraper.process_issues()
	return HttpResponseRedirect('/')