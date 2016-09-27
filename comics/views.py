from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView
from django.http import HttpResponseRedirect
from .models import Series, Issue, Character, Arc, Team, Publisher, Creator, Settings
from .utils.comicimporter import ComicImporter

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
	comicimporter = ComicImporter()
	comicimporter.import_comic_files()
	return HttpResponseRedirect('/')

def reprocess(request, issue_id):
	comicimporter = ComicImporter()
	comicimporter.reprocess_issue(issue_id)
	return HttpResponseRedirect('/issue/' + issue_id)