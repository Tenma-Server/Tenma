from __future__ import unicode_literals

import datetime,os,rarfile,zipfile,tarfile

from shutil import copyfile

from django.db import models
from solo.models import SingletonModel
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator

from .utils.comicfilehandler import ComicFileHandler

"""
Create a choice for years
"""
YEAR_CHOICES = [(r,r) for r in range(1837, datetime.date.today().year+1)]

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
	name = models.CharField('Arc name', max_length=200)
	desc = models.TextField('Description', max_length=500, blank=True)
	image = models.FilePathField('Image file path', path="media/images/arcs", blank=True)

	def __str__(self):
		return self.name

class Team(models.Model):
	cvid = models.CharField(max_length=15)
	cvurl = models.URLField(max_length=200)
	name = models.CharField('Team name', max_length=200)
	desc = models.TextField('Description', max_length=500, blank=True)
	image = models.FilePathField('Image file path', path="media/images/teams", blank=True)

	def __str__(self):
		return self.name

class Character(models.Model):
	cvid = models.CharField(max_length=15)
	cvurl = models.URLField(max_length=200)
	name = models.CharField('Character name', max_length=200)
	desc = models.TextField('Description', max_length=500, blank=True)
	teams = models.ManyToManyField(Team, blank=True)
	image = models.FilePathField('Image file path', path="media/images/characters", blank=True)

	def __str__(self):
		return self.name

class Creator(models.Model):
	cvid = models.CharField(max_length=15)
	cvurl = models.URLField(max_length=200)
	name = models.CharField('Creator name', max_length=200)
	desc = models.TextField('Description', max_length=500, blank=True)
	image = models.FilePathField('Image file path', path="media/images/creators", blank=True)

	def __str__(self):
		return self.name

class Publisher(models.Model):
	cvid = models.CharField(max_length=15)
	cvurl = models.URLField(max_length=200)
	name = models.CharField('Series name', max_length=200)
	desc = models.TextField('Description', max_length=500, blank=True)
	logo = models.FilePathField('Logo file path', path="media/images/publishers", blank=True)

	def __str__(self):
		return self.name

class Series(models.Model):
	cvid = models.CharField(max_length=15, blank=True)
	cvurl = models.URLField(max_length=200, blank=True)
	name = models.CharField('Series name', max_length=200)
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True, blank=True)
	year = models.PositiveSmallIntegerField('year', choices=YEAR_CHOICES, default=datetime.datetime.now().year, blank=True)
	desc = models.TextField('Description', max_length=500, blank=True)

	def __str__(self):
		return self.name

	def issue_numerical_order_set(self):
		return self.issue_set.all().order_by('number')
		
	class Meta:
		verbose_name_plural = "Series"

class Issue(models.Model):
	cvid = models.CharField(max_length=15, blank=True)
	cvurl = models.URLField(max_length=200, blank=True)
	series = models.ForeignKey(Series, on_delete=models.CASCADE, blank=True)
	name = models.CharField('Issue name', max_length=200, blank=True)
	number = models.PositiveSmallIntegerField('Issue number')
	date = models.DateField('Cover date', blank=True)
	desc = models.TextField('Description', max_length=500, blank=True)
	arcs = models.ManyToManyField(Arc, blank=True)
	characters = models.ManyToManyField(Character, blank=True)
	creators = models.ManyToManyField(Creator, blank=True)
	teams = models.ManyToManyField(Team, blank=True)
	file = models.FilePathField('File path', path="files/", recursive=True)
	cover = models.FilePathField('Cover file path', path="media/images/covers", blank=True)

	def __str__(self):
		return self.name

	def page_set(self):

		comicfilehandler = ComicFileHandler()
		comic = comicfilehandler.extract_comic(self.file, self.id)

		return comic