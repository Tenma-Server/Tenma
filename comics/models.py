from __future__ import unicode_literals

import datetime,os,rarfile,zipfile,tarfile

from shutil import copyfile

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.conf.urls.static import static

"""
Create a choice for years
"""
YEAR_CHOICES = [(r,r) for r in range(1837, datetime.date.today().year+1)]

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
	cvid = models.CharField(max_length=15)
	cvurl = models.URLField(max_length=200)
	name = models.CharField('Series name', max_length=200)
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, blank=True)
	year = models.PositiveSmallIntegerField('year', choices=YEAR_CHOICES, default=datetime.datetime.now().year, blank=True)
	desc = models.TextField('Description', max_length=500, blank=True)

	def __str__(self):
		return self.name

	def issue_numerical_order_set(self):
		return self.issue_set.all().order_by('number')

class Issue(models.Model):
	cvid = models.CharField(max_length=15)
	cvurl = models.URLField(max_length=200)
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
		f = self.file
		filename = os.path.basename(f)
		dirname = os.path.splitext(filename)[0]
		extension = os.path.splitext(filename)[1].lower()
		mediaroot = settings.MEDIA_ROOT + '/temp/'
		mediaurl = settings.MEDIA_URL + 'temp/' + dirname + '/'
		temppath = mediaroot + dirname
		tempfile = mediaroot + filename

		# Check if directory exists
		if os.path.isdir(temppath):
			# Check if directory is not empty
			if not os.listdir(temppath) == []:
				pages = self._get_file_list(temppath)
				return {'mediaurl': mediaurl, 'pages': pages}
			else:
				# Check if file does not exists
				if not os.path.isdir(tempfile):
					copyfile(f, tempfile)
		else:
			# Check if file exists
			if os.path.isdir(tempfile):
				os.mkdir(temppath)
			else:
				copyfile(f, tempfile)
				os.mkdir(temppath)

		########
		# Process File
		# Support TODO:
		# - CB7
		# - 7Z
		# - PDF (?)
		# - DJVU (?)
		########

		# Check for CBR or RAR
		if extension == '.cbr' or extension == '.rar':
			# Change CBR to RAR
			if extension == '.cbr':
				newext = tempfile.replace('.cbr', '.rar')
				os.rename(tempfile, newext)
				rf = rarfile.RarFile(newext)
			else:
				rf = rarfile.RarFile(tempfile)
			rf.extractall(path=temppath)
		# Check for CBZ or ZIP
		elif extension == '.cbz' or extension == '.zip':
			if extension == '.cbz':
				newext = tempfile.replace('.cbz', '.zip')
				os.rename(tempfile, newext)
				z = zipfile.ZipFile(newext)
			else:
				z = zipfile.ZipFile(tempfile)	
			z.extractall(path=temppath)
		# Check for CBT or TAR
		elif extension == '.cbt' or extension == '.tar':
			if extension == '.cbt':
				newext = tempfile.replace('.cbt', '.tar')
				os.rename(tempfile, newext)
				t = tarfile.TarFile(newext)
			else:
				t =tarfile.TarFile(tempfile)
			t.extractall(path=temppath)

		# Delete the file after extraction so that space isn't wasted.
		if os.path.isfile(tempfile):
			os.remove(tempfile)
		elif os.path.isfile(newext):
			os.remove(newext)

		# Get a list of pages
		pages = self._get_file_list(temppath)

		return {'mediaurl': mediaurl, 'pages': pages}

	def _get_file_list(self, filepath):

		pages = []

		for root, dirs, files in os.walk(filepath):
			for file in files:
				if os.path.splitext(file)[1].lower() == '.jpg' or os.path.splitext(file)[1].lower() == '.jpeg':
					path = os.path.join(root,file)
					newpath = path.replace(filepath + '/', '')
					pages.append(newpath)

		return pages