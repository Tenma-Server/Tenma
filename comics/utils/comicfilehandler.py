import os,rarfile,zipfile,tarfile,re,sys
import comics
from shutil import copyfile
from django.conf import settings
from operator import attrgetter
from . import fnameparser
from . import utils
from urllib.parse import quote

class ComicFileHandler(object):

	#==================================================================================================

	def __init__(self):
		# Set the unrar tool based on filesystem
		if sys.platform == 'win32':		# Windows
			rarfile.UNRAR_TOOL = os.path.dirname(comics.__file__) + "/utils/unrar/unrar.exe"	
		elif sys.platform == 'darwin':	# Mac
			rarfile.UNRAR_TOOL = os.path.dirname(comics.__file__) + "/utils/unrar/unrar_mac"
		elif sys.platform == 'linux2':	# Linux
			rarfile.UNRAR_TOOL = os.path.dirname(comics.__file__) + "/utils/unrar/unrar-nonfree_ubuntu"
			

	#==================================================================================================

	def extract_comic(self, file, id):
		'''
		Extract all the pages from a comic book file.

		Returns a dictionary containing the mediaurl and a list of files.
		'''
		filename = os.path.basename(file)
		ext = os.path.splitext(filename)[1].lower()
		mediaroot = settings.MEDIA_ROOT + '/temp/'
		mediaurl = settings.MEDIA_URL + 'temp/' + str(id) + '/'
		temppath = mediaroot + str(id)
		tempfile = mediaroot + filename

		# File validation
		if utils.valid_comic_file(filename):
			# If directory already exists, return it.
			# Otherwise, create the directory.
			if os.path.isdir(temppath):
				if not os.listdir(temppath) == []:
					pages = self._get_file_list(temppath)
					return {'mediaurl': mediaurl, 'pages': pages}
			else:
				os.mkdir(temppath)

			# Create temp file if not found.
			if not os.path.isfile(tempfile):
				copyfile(file, tempfile)
				os.chmod(tempfile, 0o777)

			# Change extension if needed
			comic_file = self.normalise_comic_extension(tempfile)

			# Get extractor
			extractor = self.get_extractor(comic_file)
			extractor.extractall(path=temppath)

			if ext == '.zip':
				extractor.close()

			# Delete the file after extraction so that space isn't wasted.
			if os.path.isfile(tempfile):
				os.remove(tempfile)
			elif os.path.isfile(comic_file):
				os.remove(comic_file)

			# Get a list of pages
			pages = self._get_file_list(temppath)

			for root, dirs, files in os.walk(temppath):
				for file in files:
					image_path = root + '/' + file
					utils.optimize_image(image_path, 75, 1920)

		return {'mediaurl': mediaurl, 'pages': pages}


	#==================================================================================================

	def extract_cover(self,file):
		'''
		Extract the cover image from a comic file.

		Returns a path to the cover image.
		'''
		filename = os.path.basename(file)
		ext = os.path.splitext(filename)[1].lower()
		mediaroot = settings.MEDIA_ROOT + '/images/'
		mediaurl = 'media/images/'
		tempfile = mediaroot + filename
		cover = ''

		# File validation
		if utils.valid_comic_file(filename):			
			# Copy file to temp directory
			copyfile(file, tempfile)
			os.chmod(tempfile, 0o777)

			# Change extension if needed
			comic_file = self.normalise_comic_extension(tempfile)

			# Get extractor
			extractor = self.get_extractor(comic_file)

			# Get cover file name
			first_image = self._get_first_image(extractor.namelist())
			normalised_file = self._normalise_imagepath(first_image)
			cover_filename = os.path.splitext(normalised_file)[0] + '-' + os.path.splitext(filename)[0] + os.path.splitext(normalised_file)[1]

			# Delete existing cover if it exists
			self._delete_existing_cover(mediaroot + cover_filename)

			# Extract, rename, and optimize cover image
			extractor.extract(first_image, path=mediaroot)
			os.rename(mediaroot + normalised_file, mediaroot + cover_filename)
			cover = mediaurl + cover_filename
			utils.optimize_image(cover, 75, 540)

			# Close out zip extractor
			if ext == '.zip':
				extractor.close()

			# Delete the temp comic file
			if os.path.isfile(tempfile):
				os.remove(tempfile)
			elif os.path.isfile(comic_file):
				os.remove(comic_file)	

		return cover
		

	#==================================================================================================

	def _get_file_list(self, filepath):
		'''
		Returns a sorted list of image files for a comic. Filenames are changed
		to numbers so filepaths stay short.
		'''
		pages = []

		for root, dirs, files in os.walk(filepath):
			sorted_files = sorted(files)
			i = 0
			for file in sorted_files:
				file_ext = os.path.splitext(file)[1].lower()
				if file_ext == '.jpg' or file_ext == '.jpeg' or\
				   file_ext == '.png' or file_ext == '.gif':
					path = os.path.join(root,file)
					numbered_file = "%03d" % (i,) + file_ext
					os.rename(path, filepath + '/' + numbered_file)
					i += 1
					newpath = numbered_file.replace(filepath + '/', '')
					if os.name == 'nt':
						newpath = numbered_file.replace(filepath + '\\', '')
					pages.append(quote(newpath))

		return pages


	#==================================================================================================

	def _get_first_image(self, filelist):
		''' Returns the name of the first file from a sorted list. '''

		sorted_list = sorted(filelist)

		for f in sorted_list:
			f_ext = os.path.splitext(f)[1].lower()
			if f_ext == '.jpg' or f_ext == '.jpeg' or\
			   f_ext == '.png' or f_ext == '.gif':
				return f


	#==================================================================================================

	def _delete_existing_cover(self, filepath):
		''' Deletes cover image if found. '''

		if os.path.isfile(filepath):
			os.chmod(filepath, 0o777)
			os.remove(filepath)


	#==================================================================================================

	def _normalise_imagepath(self, filepath):
		'''	Returns a normalised image path. '''
		
		path_normalise = re.compile(r"[/\\]")

		filepath_parts = path_normalise.sub("`", filepath).split('`')

		path = ''

		for part in filepath_parts:
			path = os.path.join(path, part)

		return path


	#==================================================================================================

	def normalise_comic_extension(self, comic_file):
		''' Set correct extension if necessary '''

		ext = os.path.splitext(comic_file)[1].lower()
		c = comic_file
		if ext == '.cbr':
			c = c.replace('.cbr', '.rar')
		elif ext == '.cbz':
			c = c.replace('.cbz', '.zip')
		elif ext == '.cbt':
			c = c.replace('.cbt', '.tar')
		os.rename(comic_file, c)

		return c


	#==================================================================================================

	def get_extractor(self, comic_file):
		''' Return extractor based on file extension '''

		# Get extractor
		ext = os.path.splitext(comic_file)[1].lower()
		e = None
		if ext == '.rar':
			e = rarfile.RarFile(comic_file)
		if ext == '.zip':
			e = zipfile.ZipFile(comic_file)
		if ext == '.tar':
			e = tarfile.TarFile(comic_file)

		return e