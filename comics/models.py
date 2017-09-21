from __future__ import unicode_literals

import datetime,os,rarfile,zipfile,tarfile

from shutil import copyfile
from multiselectfield import MultiSelectField
from django.db import models
from solo.models import SingletonModel
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator
from .utils.comicfilehandler import ComicFileHandler

"""
Choices for model use.
"""
# Generated years
YEAR_CHOICES = [(r,r) for r in range(1837, datetime.date.today().year+1)]

# Comic read status
STATUS_CHOICES = (
	(0, 'Unread'),
	(1, 'Partially read'),
	(2, 'Completed'),
)

# Creator roles for an issue
ROLE_CHOICES = (
	('artist', 'Artist'),
	('colorist', 'Colorist'),
	('cover', 'Cover'),
	('editor', 'Editor'),
	('inker', 'Inker'),
	('journalist', 'Journalist'),
	('letterer', 'Letterer'),
	('other', 'Other'),
	('penciler', 'Penciler'),
	('production', 'Production'),
	('writer', 'Writer'),
)

class Settings(SingletonModel):
	api_key = models.CharField(
		'ComicVine API Key',
		help_text="A 40-character key provided by ComicVine. This is used to retrieve metadata about your comics. You can create a ComicVine API Key at <a target=\"_blank\" href=\"http://comicvine.gamespot.com/api/\">ComicVine's API Page</a> (ComicVine account is required).",
		validators=[RegexValidator(
			regex='^.{40}$',
			message='Length must be 40 characters.',
			code='nomatch'
		)],
		max_length=40,
		blank=True
	)

	def __str__(self):
		return "Settings"

class Arc(models.Model):
	cvid = models.CharField(max_length=15)
	cvurl = models.URLField(max_length=200)
	name = models.CharField(max_length=200)
	desc = models.TextField(max_length=500, blank=True)
	image = models.FilePathField(path="media/images", blank=True)

	def __str__(self):
		return self.name

class Team(models.Model):
	cvid = models.CharField(max_length=15)
	cvurl = models.URLField(max_length=200)
	name = models.CharField(max_length=200)
	desc = models.TextField(max_length=500, blank=True)
	image = models.FilePathField(path="media/images", blank=True)

	def __str__(self):
		return self.name

class Character(models.Model):
	cvid = models.CharField(max_length=15)
	cvurl = models.URLField(max_length=200)
	name = models.CharField(max_length=200)
	desc = models.TextField(max_length=500, blank=True)
	teams = models.ManyToManyField(Team, related_name="characters", blank=True)
	image = models.FilePathField(path="media/images", blank=True)

	def __str__(self):
		return self.name

class Creator(models.Model):
	cvid = models.CharField(max_length=15)
	cvurl = models.URLField(max_length=200)
	name = models.CharField(max_length=200)
	desc = models.TextField(max_length=500, blank=True)
	image = models.FilePathField(path="media/images", blank=True)

	def __str__(self):
		return self.name

class Publisher(models.Model):
	cvid = models.CharField(max_length=15)
	cvurl = models.URLField(max_length=200)
	name = models.CharField(max_length=200)
	desc = models.TextField(max_length=500, blank=True)
	logo = models.FilePathField(path="media/images", blank=True)

	def __str__(self):
		return self.name

class Series(models.Model):
	cvid = models.CharField(max_length=15, blank=True)
	cvurl = models.URLField(max_length=200, blank=True)
	name = models.CharField(max_length=200)
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True, related_name="series", blank=True)
	year = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year, blank=True)
	desc = models.TextField(max_length=500, blank=True)

	def __str__(self):
		return self.name

	def issue_numerical_order_set(self):
		return self.issue_set.all().order_by('number')

	def issue_count(self):
		return self.issue_set.all().count()

	def unread_issue_count(self):
		return self.issue_set.exclude(status=2).count()

	@property
	def image(self):
		return self.issues.all().order_by('number').first().image

	class Meta:
		verbose_name_plural = "Series"

class Issue(models.Model):
	cvid = models.CharField(max_length=15, blank=True)
	cvurl = models.URLField(max_length=200, blank=True)
	series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name="issues", blank=True)
	name = models.CharField(max_length=200, blank=True)
	number = models.PositiveSmallIntegerField()
	date = models.DateField(blank=True)
	desc = models.TextField(max_length=500, blank=True)
	arcs = models.ManyToManyField(Arc, related_name="issues", blank=True)
	characters = models.ManyToManyField(Character, related_name="issues", blank=True)
	teams = models.ManyToManyField(Team, related_name="issues", blank=True)
	file = models.FilePathField(path="files/", recursive=True)
	cover = models.FilePathField(path="media/images", blank=True)
	status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0, blank=True)
	leaf = models.PositiveSmallIntegerField(editable=False, default=1, blank=True)
	page_count = models.PositiveSmallIntegerField(editable=False, default=1, blank=True)

	def __str__(self):
		return self.series.name + ' #' + str(self.number)

	def get_absolute_url(self):
		return reverse('author-detail', kwargs={'pk': self.pk})

	def page_set(self):
		comicfilehandler = ComicFileHandler()
		comic = comicfilehandler.extract_comic(self.file, self.id)
		return comic

class Roles(models.Model):
	creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
	issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
	roles = MultiSelectField(choices=ROLE_CHOICES)

	def __str__(self):
		return self.issue.series.name + ' #' + str(self.issue.number) + ' - ' + self.creator.name

	class Meta:
		verbose_name_plural = "Roles"
