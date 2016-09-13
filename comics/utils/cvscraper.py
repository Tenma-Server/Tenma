from urllib.request import urlretrieve, urlopen, Request
from urllib.parse import quote_plus, unquote_plus
from comics.models import Arc, Character, Creator, Team, Publisher, Series, Issue, Settings
from .comicfilehandler import ComicFileHandler
from . import fnameparser, utils
import json, os, time, datetime

class CVScraper(object):

	#==================================================================================================

	def __init__(self):
		# Set basic reusable strings
		self._api_key = Settings.get_solo().api_key
		self.directory_path = 'files'
		self.baseurl = 'http://comicvine.gamespot.com/api/'
		self.imageurl = 'http://comicvine.gamespot.com/api/image/'

		# Set fields to grab when calling the API.
		# This helps increase performance per call.
		self.arc_fields = '&field_list=deck,description,id,image,name,site_detail_url'
		self.character_fields = '&field_list=deck,description,id,image,name,site_detail_url'
		self.creator_fields = '&field_list=deck,description,id,image,name,site_detail_url'
		self.team_fields = '&field_list=characters,deck,description,id,image,name,site_detail_url'
		self.publisher_fields = '&field_list=deck,description,id,image,name,site_detail_url'
		self.series_fields = '&field_list=deck,description,id,name,publisher,site_detail_url,start_year'
		self.issue_fields = '&field_list=character_credits,cover_date,deck,description,id,image,issue_number,name,person_credits,site_detail_url,story_arc_credits,team_credits,volume'


	#==================================================================================================

	def process_issues(self):
		# Settings for comics directory
		processed_files_file = os.path.join(self.directory_path, '.processed')

		# Create processed files file
		if not os.path.isfile(processed_files_file):
			file = open(processed_files_file, 'w')

		processed_files = set(line.strip() for line in open(processed_files_file))

		# Check for unprocessed files
		with open(processed_files_file, "a") as pff:
			for root, disr, files in os.walk(self.directory_path):
				for file in files:
					time.sleep(1)
					if file not in processed_files:
						# Make sure the file is valid
						if file.endswith(".cbz") or file.endswith(".zip") or \
						   file.endswith(".cbr") or file.endswith(".rar") or \
						   file.endswith(".cbt") or file.endswith(".tar"): 

							# Attempt to find match
							if not self._api_key == '':
								cvid = self._find_match(file)
							else:
								cvid = ''

							if not cvid == '':
								# Scrape the issue
								self._scrape_issue(file, cvid)
								# Write to the .processed file
								pff.write("%s\n" % file)
							else:
								# Create issue without cvid
								self._create_issue_without_cvid(file)


	#==================================================================================================

	def _find_match(self, filename):
		# Initialize response
		cvid = ''

		# Query Settings
		query_fields = '&field_list=cover_date,id,issue_number,name,volume'
		query_limit = '&limit=100'

		# Attempt to extract series name, issue number, and year
		extracted = fnameparser.extract(filename)
		series_name = extracted[0]
		series_name_url = quote_plus(series_name)
		issue_number = extracted[1]
		issue_year = extracted[2]

		# First check if there's already a series locally
		matching_series = Series.objects.filter(name=series_name)

		if matching_series:
			if not matching_series[0].cvid == '':
				cvid = self._find_match_with_series(matching_series[0].cvid, issue_number)
				if not cvid == '':
					return cvid

		# Attempt to find issue based on extracted Series Name and Issue Number
		query_url = self.baseurl + 'search?format=json&resources=issue' + '&api_key=' + self._api_key + query_fields + query_limit + '&query='


		# Check for series name and issue number, or just series name
		if series_name and issue_number:
			query_url = query_url + series_name_url + '%20%23' + issue_number
			query_request = Request(query_url)
			query_response = json.loads(urlopen(query_request).read().decode('utf-8'))
		elif series_name:
			query_url = query_url + series_name_url
			query_request = Request(query_url)
			query_response = json.loads(urlopen(query_request).read().decode('utf-8'))

		best_option_list = []

		# Try to find the closest match.
		for issue in query_response['results']:
			item_year = issue['cover_date'][0:4] if issue['cover_date'] else ''
			item_number = issue['issue_number'] if issue['issue_number'] else ''
			item_name = issue['volume']['name'] if issue['volume']['name'] else ''

			if series_name and issue_number and issue_year:
				if item_name == series_name and item_number == issue_number and item_year == issue_year:
					best_option_list.insert(0, issue['id'])
					break
				elif item_name == series_name and item_number == issue_number:
					best_option_list.insert(0, issue['id'])
			elif series_name and issue_number:
				if item_name == series_name and item_number == issue_number:
					best_option_list.insert(0, issue['id'])
		#	
		#	elif series_name:
		#		if item_name == series_name and issue['volume']['count_of_issues'] == '1':
		#			best_option_list.append(issue['id'])

		return best_option_list[0] if best_option_list else ''

	#==================================================================================================

	def _find_match_with_series(self, series_cvid, issue_number):

		issue_cvid = ''

		if issue_number:
			# Query Settings
			query_fields = '&field_list=issues'

			# Attempt to find issue based on extracted Series Name and Issue Number
			query_request = Request(self.baseurl + 'volume/4050-' + series_cvid + '?format=json&api_key=' + self._api_key + query_fields)
			query_response = json.loads(urlopen(query_request).read().decode('utf-8'))

			# Try to find the closest match.
			for issue in query_response['results']['issues']:
				item_number = issue['issue_number'] if issue['issue_number'] else ''
				if item_number == issue_number:
					issue_cvid = issue['id']

		return issue_cvid

	#==================================================================================================

	def _create_issue_without_cvid(self, filename):

		# Make sure the issue hadn't already been added
		matching_issue = Issue.objects.filter(file=os.path.join(self.directory_path, filename))

		if not matching_issue:
			# Attempt to extract series name, issue number, and year
			extracted = fnameparser.extract(filename)
			series_name = extracted[0]
			issue_number = extracted[1]
			issue_year = extracted[2]

			# 1. Set basic issue information:
			issue = Issue()
			issue.file = os.path.join(self.directory_path, filename)

			if issue_number:
				issue.number = issue_number
			else:
				issue.number = 1

			if issue_year:
				issue.date = issue_year + '-01-01'
			else:
				issue.date = datetime.date.today()

			cfh = ComicFileHandler()
			issue.cover = cfh.extract_cover(os.path.join(self.directory_path, filename))

			# 2. Set Series info:
			matching_series = Series.objects.filter(name=series_name)

			if not matching_series:
				series = Series()
				series.name = series_name

				# 4. Save Series
				series.save()
				issue.series = series

			else:
				issue.series = matching_series[0]

			# 5. Save issue.
			issue.save()

	#==================================================================================================

	def _scrape_issue(self, filename, cvid):
		# Make API call and store issue response
		time.sleep(1)
		request_issue = Request(self.baseurl + 'issue/4000-' + str(cvid) + '/?format=json&api_key=' + self._api_key + self.issue_fields)
		response_issue = json.loads(urlopen(request_issue).read().decode('utf-8'))
		issue_data = self._get_object_data(response_issue['results'])

		# 1. Set basic issue information:
		issue = Issue()

		issue.file = os.path.join(self.directory_path, filename)
		issue.cvid = issue_data['cvid']
		issue.cvurl = issue_data['cvurl']
		issue.name = issue_data['name']
		issue.desc = issue_data['desc']
		issue.number = issue_data['number']
		issue.date = issue_data['date']
		issue.cover = issue_data['image']

		# 2. Set Series info:
		matching_series = Series.objects.filter(cvid=response_issue['results']['volume']['id'])

		if not matching_series:
			time.sleep(1)

			series = Series()
			
			request_series = Request(response_issue['results']['volume']['api_detail_url'] + '?format=json&api_key=' + self._api_key + self.series_fields)
			response_series = json.loads(urlopen(request_series).read().decode('utf-8'))
			series_data = self._get_object_data(response_series['results'])

			series.cvid = series_data['cvid']
			series.cvurl = series_data['cvurl']
			series.name = series_data['name']
			series.desc = series_data['desc']
			series.year = series_data['year']

			# 3. Set Publisher info:
			matching_publisher = Publisher.objects.filter(cvid=response_series['results']['publisher']['id'])

			if not matching_publisher:
				time.sleep(1)

				publisher = Publisher()

				# Store publisher response
				request_publisher = Request(response_series['results']['publisher']['api_detail_url'] + '?format=json&api_key=' + self._api_key + self.publisher_fields)
				response_publisher = json.loads(urlopen(request_publisher).read().decode('utf-8'))
				publisher_data = self._get_object_data(response_publisher['results'])

				publisher.cvid = publisher_data['cvid']
				publisher.cvurl = publisher_data['cvurl']
				publisher.name = publisher_data['name']
				publisher.desc = publisher_data['desc']
				publisher.logo = publisher_data['image']

				publisher.save()
				series.publisher = publisher

			else:
				series.publisher = matching_publisher[0]

			series.save()
			issue.series = series

		else:
			issue.series = matching_series[0]

		# 4. Save issue.
		issue.save()

		# 5. Set Arcs info
		for story_arc in response_issue['results']['story_arc_credits']:
			time.sleep(1)

			# Check to make sure the series doesn't already exist.
			matching_arc = Arc.objects.filter(cvid=story_arc['id'])

			if not matching_arc:
				# Store Arc response
				request_arc = Request(story_arc['api_detail_url'] + '?format=json&api_key=' + self._api_key + self.arc_fields)
				response_arc = json.loads(urlopen(request_arc).read().decode('utf-8'))
				arc_data = self._get_object_data(response_arc['results'])

				# Create Arc
				issue.arcs.create(
					cvid=arc_data['cvid'],
					cvurl=arc_data['cvurl'],
					name=arc_data['name'],
					desc=arc_data['desc'] ,
					image=arc_data['image'],
				)

			else:
				# Add found Arc to dictionary
				issue.arcs.add(matching_arc[0])

		# 6. Set Characters info
		for character in response_issue['results']['character_credits']:
			time.sleep(1)

			# Check to make sure the character doesn't already exist.
			matching_character = Character.objects.filter(cvid=character['id'])

			if not matching_character:
				# Store Character response
				request_character = Request(character['api_detail_url'] + '?format=json&api_key=' + self._api_key + self.character_fields)
				response_character = json.loads(urlopen(request_character).read().decode('utf-8'))
				character_data = self._get_object_data(response_character['results'])

				# Create Character
				issue.characters.create(
					cvid=character_data['cvid'],
					cvurl=character_data['cvurl'],
					name=character_data['name'],
					desc=character_data['desc'],
					image=character_data['image'],
				)

			else:
				# Add found Character to Issue
				issue.characters.add(matching_character[0])

		# 7. Set Creators info
		for person in response_issue['results']['person_credits']:
			time.sleep(1)

			# Check to make sure the character doesn't already exist.
			matching_creator = Creator.objects.filter(cvid=person['id'])

			if not matching_creator:
				# Store Creator response
				request_creator = Request(person['api_detail_url'] + '?format=json&api_key=' + self._api_key + self.creator_fields)
				response_creator = json.loads(urlopen(request_creator).read().decode('utf-8'))
				creator_data = self._get_object_data(response_creator['results'])

				# Create Creator
				issue.creators.create(
					cvid=creator_data['cvid'],
					cvurl=creator_data['cvurl'],
					name=creator_data['name'],
					desc=creator_data['desc'],
					image=creator_data['image'],
				)

			else:
				# Add found Character to Issue
				issue.creators.add(matching_creator[0])

		# 8. Set Teams info
		for team in response_issue['results']['team_credits']:
			time.sleep(1)

			matching_team = Team.objects.filter(cvid=team['id'])

			if not matching_team:
				request_team = Request(team['api_detail_url'] + '?format=json&api_key=' + self._api_key + self.team_fields)
				response_team = json.loads(urlopen(request_team).read().decode('utf-8'))
				team_data = self._get_object_data(response_team['results'])

				# Create Creator
				issue.teams.create(
					cvid=team_data['cvid'],
					cvurl=team_data['cvurl'],
					name=team_data['name'],
					desc=team_data['desc'],
					image=team_data['image'],
				)

				for character in response_team['results']['characters']:
					matching_character = Character.objects.filter(cvid=character['id'])
					if matching_character:
						team_item = Team.objects.filter(cvid=team['id'])
						matching_character[0].teams.add(team_item[0])

			else:
				issue.teams.add(matching_team[0])

	#==================================================================================================

	def _get_object_data(self, response):
		''' 
		Gathers object data from a response. Tests each value to make sure 
		it exists in the response before trying to set it. 

		CVID and CVURL will always exist in a ComicVine response, so there
		is no need to verify this data.

		Returns a dictionary with all the gathered data.
		'''
		
		# Get Name
		name = ''

		if 'name' in response:
			if response['name']:
				name = response['name']

		# Get Start Year (only exists for Series objects)
		year = ''

		if 'start_year' in response:
			if response['start_year']:
				year = response['start_year']

		# Get Number (only exists for Issue objects)
		number = ''

		if 'issue_number' in response:
			if response['issue_number']:
				number = response['issue_number']

		# Get Date (only exists for Issue objects)
		date = ''

		if 'cover_date' in response:
			if response['cover_date']:
				date = response['cover_date']


		# Get Description (Favor short description if available)
		desc = ''

		if 'deck' in response:
			if response['deck']:
				desc = response['deck']
		elif 'description' in response:
			if response['description']:
				desc = response['description']

		# Get Image
		image = ''

		if 'image' in response:
			if response['image']:
				image_url = self.imageurl + response['image']['super_url'].rsplit('/', 1)[-1]
				image_filename = unquote_plus(image_url.split('/')[-1])
				image = utils.test_image(urlretrieve(image_url, 'media/images/' + image_filename)[0])

		# Create Character
		data = {
			'cvid': response['id'],  				# Always exists
			'cvurl': response['site_detail_url'],  	# Always exists
			'name': name,
			'year': year,
			'number': number,
			'date': date,
			'desc': desc,
			'image': image,
		}

		return data