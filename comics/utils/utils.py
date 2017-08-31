#coding: utf-8
'''
This is a modified version of cbanack's utils module from his
ComicVineScraper plugin (https://github.com/cbanack/comic-vine-scraper)

This module contains a variety of generally useful utility methods.

@author: Cory Banack

Originally modified on Aug 10, 2016
@author: hmhrex
'''

import re,sys,os
from PIL import Image

# unmodifiable cache for speeding up calls to natural_compare
__keys_cache = None


#==============================================================================
def is_string(object):
   ''' returns a boolean indicating whether the given object is a string '''

   if object is None:
      return False
   return isinstance(object, str)


#==============================================================================
def is_number(s):
   ''' returns a boolean indicating whether the given object is a number, or
       a string that can be converted to a number. '''
   try:
      float(s)
      return True
   except:
      return False


#==============================================================================
def sstr(object):
   ''' safely converts the given object into a string (sstr = safestr) '''
   if object is None:
      return '<None>'
   if is_string(object):
      # this is needed, because str() breaks on some strings that have unicode
      # characters, due to a python bug.  (all strings in python are unicode.)
      return object
   return str(object)


# ==========================================================================
def natural_compare(a, b):
   '''
   Compares two strings using their "natural" ordering. Strings that don't
   contain numbers will sort alphabetically, but strings with numbers will
   sort numerically first (["1","2" "11"] instead of ["1","11" "2"]).
   Natural comparison works between numerical strings with alphabetic characters
   (["4","4a","5"]) and even provides meaningful comparisons between numerical
   strings containing unicode fractions (["5", "5¼", "5½", "6"]).

   Returns -1 if a<b, +1 if a>b, and 0 if a==b.
   '''

   global __keys_cache
   if __keys_cache is None:
      __keys_cache = { str(x): natural_key(str(x)) for x in range(999) }

   a = __keys_cache[a] if a in __keys_cache else natural_key(a)
   b = __keys_cache[b] if b in __keys_cache else natural_key(b)
   return -1 if a < b else 1 if a > b else 0


# ==========================================================================
def natural_key(s):
   '''
   Calculates the natural sort order key for the give string.   Two strings
   that are 'naturally' identical will have identical keys, i.e. '1' and '1.0'
   or '5 A' and '5A' or '.5' and '0.5000'.
   '''
   s = s.strip()

   # Converts unicode fractions (like '5½') into floats (like 5.5).
   def unicode_fraction_to_float(s):
      number = None
      match = re.match("\s*(-?)\s*(\d*)\s*([⅛⅙⅕¼⅓⅜⅖½⅗⅝⅔¾⅘⅚⅞])\s*", s)
      if match:
         negative = match.group(1)
         intpart = match.group(2)
         intpart = float(intpart) if is_number(intpart) else 0
         fracs = {"⅛":1.0/8 ,"⅙":1.0/6,"⅕":0.2,"¼":0.25,"⅓":1.0/3,
                  "⅜":3.0/8, "⅖":0.4,"½":0.5,"⅗":0.6,"⅝":5.0/8,
                  "⅔":2.0/3,"¾":0.75,"⅘":0.8,"⅚":5.0/6,"⅞":7.0/8}
         fracpart = match.group(3)
         fracpart = fracs[fracpart] if fracpart in fracs else 0
         number = -1*(intpart+fracpart) if negative else intpart+fracpart
      return number

   unicode_float = unicode_fraction_to_float(s)
   if unicode_float:
      return ['', unicode_float, '' ]
   else:
      pattern = r'((?:^\s*-)?(?:(?:\d+\.\d+)|(?:\.\d+)|(?:\d+\.)|(?:\d+)))'
      convert = lambda text: float(text) if is_number(text) \
         else text.lower().strip()
      return [ convert(c) for c in re.split( pattern, s) ]


#==============================================================================
def convert_roman_numerals(num_s):
   '''
   Converts the given string into an positive or negative integer value,
   throwing an exception if it can't.  The given string can be a integer value
   in regular arabic form (1, 2, 3,...) or roman form (i, ii, iii, iv,...).
   The returned value will be an integer.

   Note that roman numerals outside the range [-20, 20] and 0 are not supported.
   '''

   roman_mapping = {'i':1, 'ii':2,'iii':3,'iv':4,'v':5,'vi':6,'vii':7,'viii':8,
                    'ix':9,'x':10,'xi':11,'xii':12,'xiii':13,'xiv':14,'xv':15,
                    'xvi':16,'xvii':17,'xviii':18,'xix':19,'xx':20}

   num_s = num_s.replace(' ', '').strip().lower();
   negative = num_s.startswith('-')
   if negative:
      num_s = num_s[1:]

   retval = None
   try:
      retval = int(num_s)
   except:
      retval = roman_mapping[num_s]

   return retval * -1 if negative else retval


#==============================================================================
def convert_number_words(phrase_s, expand_b):
   """
   Converts all of the number words (as defined by regular expression 'words')
   in the given phrase, either expanding or contracting them as specified.
   When expanding, words like '1' and '2nd' will be transformed into 'one'
   and 'second' in the returned string.   When contracting, the transformation
   goes in reverse.

   This method only works for numbers up to 20, and it only works properly
   on lower case strings.
   """
   number_map = {'0': 'zero', '1': 'one', '2': 'two', '3': 'three',\
      '4': 'four', '5': 'five', '6': 'six','7': 'seven', '8': 'eight',\
      '9': 'nine', '10': 'ten', '11': 'eleven', '12': 'twelve',\
      '13': 'thirteen', '14': 'fourteen', '15': 'fifteen',\
      '16': 'sixteen', '17': 'seventeen', '18': 'eighteen', '19': 'nineteen',\
      '20': 'twenty', '0th': 'zeroth', '1rst': 'first', '2nd': 'second',\
      '3rd': 'third', '4th': 'fourth', '5th': 'fifth', '6th': 'sixth',\
      '7th': 'seventh', '8th': 'eighth', '9th': 'ninth', '10th': 'tenth',\
      '11th': 'eleventh', '12th': 'twelveth', '13th': 'thirteenth',\
      '14th': 'fourteenth', '15th': 'fifteenth', '16th': 'sixteenth',\
      '17th': 'seventeenth', '18th': 'eighteenth', '19th': 'nineteenth',\
      '20th': 'twentieth'}

   b = r'\b'
   if expand_b:
      for (x,y) in number_map.iteritems():
         phrase_s = re.sub(b+x+b, y, phrase_s);
      phrase_s = re.sub(r'\b1st\b', 'first', phrase_s);
   else:
      for (x,y) in number_map.iteritems():
         phrase_s = re.sub(b+y+b, x, phrase_s);
      phrase_s = re.sub(r'\btwelfth\b', '12th', phrase_s);
      phrase_s = re.sub(r'\beightteenth\b', '18th', phrase_s);
   return phrase_s

#==============================================================================
def remove_special_characters(string):
   """
   Removes any special characters from a string.
   """
   s = re.sub('[^A-Za-z0-9\s]+', '', string)
   s = re.sub('\s+', ' ', s)
   return s


#==============================================================================
def test_image(image_path):
   ''' returns a filepath string if the file is valid and not broken '''

   path = ''

   try:
      img = Image.open(image_path)
      img.verify()
      path = image_path
   except Exception:
      pass

   return path


#==============================================================================
def optimize_image(image_path, output_quality, base_width):
   ''' Optimizes image and returns a filepath string '''

   img = Image.open(image_path)

   # Check that it's a supported format
   format = str(img.format)
   if format == 'PNG' or format == 'JPEG':
      if base_width < img.size[0]:
         wpercent = (base_width/float(img.size[0]))
         hsize = int((float(img.size[1])*float(wpercent)))
         img = img.resize((base_width,hsize), Image.BICUBIC)
      # The 'quality' option is ignored for PNG files
      img.save(image_path, quality=output_quality, optimize=True)

   return image_path


#==============================================================================
def valid_comic_file(comic_file):
   ''' Checks for valid comic file '''

   ext = os.path.splitext(comic_file)[1].lower()

   if ext == '.cbr' or ext == '.rar' or \
      ext == '.cbz' or ext == '.zip' or \
      ext == '.cbt' or ext == '.tar' or \
	  ext == '.pdf':
      return True
   else:
      return False

   # ==============================================================================
def valid_image_file(image_file):
   ''' Checks for valid image file based on file extension'''

   file_ext = os.path.splitext(image_file)[1].lower()

   if file_ext == '.jpg' or file_ext == '.jpeg' or \
      file_ext == '.png' or file_ext == '.gif':
       return True
   else:
       return False


#==============================================================================
def parse_CV_HTML(string):
   '''
   Parses a string retrieved from ComicVine and parses out unneccessary HTML.
   This is based on the ComicVine text editor.

   Returns parsed string.
   '''

   # Remove <h2>, <h3>, <h4>, <ul>, <ol>, <table> and <figure> tags
   parsed = re.sub('<(table|figure|h2|h3|h4|ul|ol)[^>]*>[\s\S]*?</(table|figure|h2|h3|h4|ul|ol)>', '', string)

   # Unpack <a> tags first because there could be other tags inside.
   parsed = re.sub('</?a[^>]*>', '', parsed)                            # Unpack <a> tags
   parsed = re.sub('</?(b|i|u|s|em|blockquote|strong)>', '', parsed)    # Unpack <b>, <i>, <u>, <s>, <em>, <blockquote> and <strong> tags

   return parsed

#==============================================================================
def extract_images_from_PDF(file, destination):
	'''
	Extracts images from a PDF.
	Uses Ned Batchelder's method: https://nedbatchelder.com/blog/200712/extracting_jpgs_from_pdfs.html
	'''

	with open(file, "rb") as f:
		pdf = f.read()

	i = 0
	njpg = 0

	while True:
		istream = pdf.find(b"stream", i)
		if istream < 0:
			break

		istart = pdf.find(b"\xff\xd8", istream, istream + 20)
		if istart < 0:
			i = istream + 20
			continue

		iend = pdf.find(b"endstream", istart)
		if iend < 0:
			raise Exception("Didn't find end of stream!")
		iend = pdf.find(b"\xff\xd9", iend - 20)
		if iend < 0:
			raise Exception("Didn't find end of JPG!")

		iend += 2
		jpg = pdf[istart:iend]
		jpgname = destination + "/%03d.jpg" % njpg
		with open(jpgname, "wb") as jpgfile:
			jpgfile.write(jpg)

		# Make sure the image isn't a thumbnail.
		img = Image.open(jpgname)
		if img.size[1] < 200:
			img.close()
			os.remove(jpgname)
			i = istream + 20
			continue

		img.close()

		njpg += 1
		i = iend

	f.close()

#==============================================================================
def extract_first_image_from_PDF(file, destination):
	'''
	Extracts first image from a PDF.
	Uses Ned Batchelder's method: https://nedbatchelder.com/blog/200712/extracting_jpgs_from_pdfs.html

	Returns cover file name.
	'''

	with open(file, "rb") as f:
		pdf = f.read()

	i = 0

	base = os.path.basename(file)
	filename = os.path.splitext(base)[0]
	jpgname = "cover-" + filename + ".jpg"
	jpgpath = destination + jpgname

	while True:
		istream = pdf.find(b"stream", i)
		if istream < 0:
			break

		istart = pdf.find(b"\xff\xd8", istream, istream + 20)
		if istart < 0:
			i = istream + 20
			continue

		iend = pdf.find(b"endstream", istart)
		if iend < 0:
			raise Exception("Didn't find end of stream!")
		iend = pdf.find(b"\xff\xd9", iend - 20)
		if iend < 0:
			raise Exception("Didn't find end of JPG!")

		iend += 2
		jpg = pdf[istart:iend]
		size = iend - istart
		if size >= 10000:
			with open(jpgpath, "wb") as jpgfile:
				jpgfile.write(jpg)

		i = iend

	f.close()

	return jpgname

#==============================================================================
def get_PDF_page_count(file):
	'''
	Gets  and returns page count from PDF file.
	'''

	page_count = 0

	with open(file, "rb") as f:
		pdf = f.read()

	i = 0

	while True:
		istream = pdf.find(b"stream", i)
		if istream < 0:
			break

		istart = pdf.find(b"\xff\xd8", istream, istream + 20)
		if istart < 0:
			i = istream + 20
			continue

		iend = pdf.find(b"endstream", istart)
		if iend < 0:
			raise Exception("Didn't find end of stream!")
		iend = pdf.find(b"\xff\xd9", iend - 20)
		if iend < 0:
			raise Exception("Didn't find end of JPG!")

		iend += 2
		jpg = pdf[istart:iend]
		size = iend - istart
		if size >= 10000:
			page_count +=  1

		i = iend

	f.close()

	return page_count
