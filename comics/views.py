from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseRedirect, JsonResponse
from .models import Series, Issue, Character, Arc, Team, Publisher, Creator, Settings, Roles
from .tasks import import_comic_files_task, reprocess_issue_task
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

	def get_context_data(self, **kwargs):
		context = super(IssueView, self).get_context_data(**kwargs)
		issue = self.get_object()
		context['roles_list'] = Roles.objects.filter(issue=issue)
		return context

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
		roles = Roles.objects.filter(creator=creator)
		context['issue_list'] = Issue.objects.filter(id__in=roles.values('issue_id'))
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

class IssueDeleteView(DeleteView):
	model = Issue
	success_url = '/'

def read(request, slug):
	issue = get_object_or_404(Issue, slug=slug)
	return render(request, 'comics/read.html', {'issue': issue})

def importer(request):
	import_comic_files_task.delay()
	return HttpResponseRedirect('/')

def reprocess(request, slug):
	reprocess_issue_task.delay(slug)
	return HttpResponseRedirect('/issue/' + slug)

def update_issue_status(request, slug):
	issue = Issue.objects.get(slug=slug)

	if request.GET.get('complete', '') == '1':
		issue.leaf = 1
		issue.status = 2
		issue.save()
	else:
		issue.leaf = int(request.GET.get('leaf', ''))
		issue.status = 1
		issue.save()

	data = { 'saved': 1 }

	return JsonResponse(data)
