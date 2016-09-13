import os,rarfile,zipfile,tarfile,re
import comics
from shutil import copyfile
from django.conf import settings
from operator import attrgetter
from . import fnameparser
from urllib.parse import quote

class ComicFileHandler(object):

	#==================================================================================================

	def __init__(self):
		if os.name == 'nt':
			rarfile.UNRAR_TOOL = os.path.dirname(comics.__file__) + "/utils/unrar/unrar.exe"	
		else:
			rarfile.UNRAR_TOOL = os.path.dirname(comics.__file__) + "/utils/unrar/unrar"
			
	#==================================================================================================

	def extract_comic(self, file, id):
		filename = os.path.basename(file)
		dirname = os.path.splitext(filename)[0]
		extension = os.path.splitext(filename)[1].lower()
		mediaroot = settings.MEDIA_ROOT + '/temp/'
		mediaurl = settings.MEDIA_URL + 'temp/' + str(id) + '/'
		temppath = mediaroot + str(id)
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
					copyfile(file, tempfile)
		else:
			# Check if file exists
			if os.path.isdir(tempfile):
				os.mkdir(temppath)
			else:
				copyfile(file, tempfile)
				os.mkdir(temppath)

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
			z.close()
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

	#==================================================================================================

	def extract_cover(self,file):
		filename = os.path.basename(file)
		covername = os.path.splitext(filename)[0]
		extension = os.path.splitext(filename)[1].lower()
		mediaroot = settings.MEDIA_ROOT + '/images/covers/'
		mediaurl = 'media/images/covers/'
		tempfile = mediaroot + filename
		extracted = mediaroot + covername

		cover_filename = ''

		# Check for CBR or RAR
		if extension == '.cbr' or extension == '.rar':
			# Change CBR to RAR
			if extension == '.cbr':
				copyfile(file, tempfile)
				newext = tempfile.replace('.cbr', '.rar')
				os.rename(tempfile, newext)
				rf = rarfile.RarFile(newext)
			else:
				rf = rarfile.RarFile(file)

			cover_filename = self._get_first_image(rf.namelist())

			rf.extract(cover_filename, path=mediaroot)

		# Check for CBZ or ZIP
		elif extension == '.cbz' or extension == '.zip':
			if extension == '.cbz':
				copyfile(file, tempfile)
				newext = tempfile.replace('.cbz', '.zip')
				os.rename(tempfile, newext)
				z = zipfile.ZipFile(newext)
			else:
				z = zipfile.ZipFile(file)	

			cover_filename = self._get_first_image(z.namelist())

			z.extract(cover_filename, path=mediaroot)
			z.close()

		# Check for CBT or TAR
		elif extension == '.cbt' or extension == '.tar':
			if extension == '.cbt':
				copyfile(file, tempfile)
				newext = tempfile.replace('.cbt', '.tar')
				os.rename(tempfile, newext)
				t = tarfile.TarFile(newext)
			else:
				t =tarfile.TarFile(file)

			cover_filename = self._get_first_image(t.namelist())

			t.extract(cover_filename, path=mediaroot)

		# Delete the file after extraction so that space isn't wasted.
		if os.path.isfile(tempfile):
			os.remove(tempfile)
		elif os.path.isfile(newext):
			os.remove(newext)

		return mediaurl + self._normalise_imagepath(cover_filename)
		
	#==================================================================================================

	def _get_file_list(self, filepath):

		pages = []

		for root, dirs, files in os.walk(filepath):
			for file in files:
				file_ext = os.path.splitext(file)[1].lower()
				if file_ext == '.jpg' or file_ext == '.jpeg':
					path = os.path.join(root,file)
					newpath = path.replace(filepath + '/', '')
					if os.name == 'nt':
						newpath = path.replace(filepath + '\\', '')
					pages.append(quote(newpath, safe='\\\\'))

		return sorted(pages)

	#==================================================================================================

	def _get_first_image(self, filelist):

		sorted_list = sorted(filelist)

		for f in sorted_list:
			f_ext = os.path.splitext(f)[1].lower()
			if f_ext == '.jpg' or f_ext == '.jpeg':
				return f

	#==================================================================================================

	def _normalise_imagepath(self, filepath):

		path_normalise = re.compile(r"[/\\]")

		filepath_parts = path_normalise.sub("#", filepath).split('#')

		path = ''

		for part in filepath_parts:
			path = os.path.join(path, part)

		return path
