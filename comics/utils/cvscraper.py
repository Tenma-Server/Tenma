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
		''' Main function to process issues in the comics directories. '''

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
							if self._api_key != '':
								cvid = self._find_match(file)
							else:
								cvid = ''

							if cvid != '':
								# Scrape the issue
								self._scrape_issue(file, cvid)
								# Write to the .processed file
								pff.write("%s\n" % file)
							else:
								# Create issue without cvid
								self._create_issue_without_cvid(file)


	#==================================================================================================

	def reprocess_issue(self, issue_id):
		''' Reprocess an existing issue in the comics directories. '''

		processed_files_file = os.path.join(self.directory_path, '.processed')
		processed_files = set(line.strip() for line in open(processed_files_file))

		issue = Issue.objects.get(id=issue_id)
		cvid = ''

		# Check if there's already a cvid.
		if issue.cvid and issue.cvid != '':
			cvid = issue.cvid
		else:
			# Attempt to find match
			if self._api_key != '':
				cvid = self._find_match(issue.file)
			else:
				cvid = ''

		# Update issue
		with open(processed_files_file, "a") as pff:
			if cvid != '':
				# Scrape the issue
				self._scrape_issue(issue.file, cvid)
				# Write to the .processed file
				if issue.file not in processed_files:
					pff.write("%s\n" % issue.file)


	#==================================================================================================

	def _find_match(self, filename):
		'''
		Try to find a match in ComicVine for an issue.

		Returns a ComicVine ID.
		'''

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
		'''
		Try to retrieve a match based on an existing series name.
		
		Returns a ComicVine ID.
		'''

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
		'''	Create an issue without a ComicVine ID.	'''

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
		'''	Creates or updates metadata from ComicVine for an Issue. '''

		# 1. Make initial API call
		issue_api_url = self.baseurl + 'issue/4000-' + str(cvid)
		request_issue = Request(issue_api_url + '/?format=json&api_key=' + self._api_key + self.issue_fields)
		response_issue = json.loads(urlopen(request_issue).read().decode('utf-8'))

		# 2. Set Series
		matching_series = Series.objects.filter(cvid=response_issue['results']['volume']['id'])

		if not matching_series:
			series = self._create_series(response_issue['results']['volume']['api_detail_url'])
		else:
			series = self._update_series(matching_series[0].id, response_issue['results']['volume']['api_detail_url'])

		# 3. Set Issue
		matching_issue = Issue.objects.filter(file=filename)

		if not matching_issue:		
			issue = self._create_issue(os.path.join(self.directory_path, filename), issue_api_url, series.id)
		else:
			issue = self._update_issue(matching_issue[0].id, issue_api_url, series.id)

		# 4. Set Publisher
		request_series = Request(response_issue['results']['volume']['api_detail_url'] + '?format=json&api_key=' + self._api_key + '&field_list=publisher')
		response_series = json.loads(urlopen(request_series).read().decode('utf-8'))

		matching_publisher = Publisher.objects.filter(cvid=response_series['results']['publisher']['id'])

		if not matching_publisher:
			self._create_publisher(response_series['results']['publisher']['api_detail_url'], issue.series.id)
		else:
			issue.series.publisher = self._update_publisher(matching_publisher[0].id, response_series['results']['publisher']['api_detail_url'])

		# 5. Set Arcs
		for story_arc in response_issue['results']['story_arc_credits']:
			matching_arc = Arc.objects.filter(cvid=story_arc['id'])
			if not matching_arc:
				self._create_arc(story_arc['api_detail_url'], issue.id)
			else:
				issue.arcs.add(self._update_arc(matching_arc[0].id, story_arc['api_detail_url']))

		# 6. Set Characters
		for character in response_issue['results']['character_credits']:
			matching_character = Character.objects.filter(cvid=character['id'])
			if not matching_character:
				self._create_character(character['api_detail_url'], issue.id)
			else:
				issue.characters.add(self._update_character(matching_character[0].id, character['api_detail_url']))

		# 7. Set Creators
		for person in response_issue['results']['person_credits']:
			matching_creator = Creator.objects.filter(cvid=person['id'])
			if not matching_creator:
				self._create_creator(person['api_detail_url'], issue.id)
			else:
				issue.creators.add(self._update_creator(matching_creator[0].id, person['api_detail_url']))

		# 8. Set Teams
		for team in response_issue['results']['team_credits']:
			matching_team = Team.objects.filter(cvid=team['id'])
			if not matching_team:
				self._create_team(team['api_detail_url'], issue.id)
			else:
				issue.teams.add(self._update_team(matching_team[0].id, team['api_detail_url']))


	#==================================================================================================

	def _get_object_data(self, response):
		''' 
		Gathers object data from a response and tests each value to make sure 
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
		if desc == '':
			if 'description' in response:
				if response['description']:
					desc = response['description']

		# Get Image
		image = ''

		if 'image' in response:
			if response['image']:
				image_url = self.imageurl + response['image']['super_url'].rsplit('/', 1)[-1]
				image_filename = unquote_plus(image_url.split('/')[-1])
				image = utils.test_image(urlretrieve(image_url, 'media/images/' + image_filename)[0])

		# Create data object
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


	#==================================================================================================

	def _create_arc(self, api_url, issue_id):
		''' 
		Creates Arc from ComicVine API URL and adds it to
		it's corresponding Issue.

		Returns the Arc object created.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.arc_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		issue = Issue.objects.get(id=issue_id)

		# Create Arc
		a = issue.arcs.create(
			cvid=data['cvid'],
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			image=data['image'],
		)

		return a


	#==================================================================================================

	def _create_character(self, api_url, issue_id):
		''' 
		Creates Character from ComicVine API URL and adds it to
		it's corresponding Issue.

		Returns the Character object created.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.character_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		issue = Issue.objects.get(id=issue_id)

		# Create Character
		ch = issue.characters.create(
			cvid=data['cvid'],
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			image=data['image'],
		)

		return ch


	#==================================================================================================

	def _create_creator(self, api_url, issue_id):
		''' 
		Creates Creator from ComicVine API URL and adds it to
		it's corresponding Issue.

		Returns the Creator object created.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.creator_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		issue = Issue.objects.get(id=issue_id)

		# Create Creator
		cr = issue.creators.create(
			cvid=data['cvid'],
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			image=data['image'],
		)

		return cr


	#==================================================================================================

	def _create_issue(self, file, api_url, series_id):
		''' 
		Creates Issue from ComicVine API URL and adds the 
		corresponding Series.

		Returns the Issue object created.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.issue_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		series = Series.objects.get(id=series_id)

		# Create Issue
		i = Issue.objects.create(
			cvid=data['cvid'],
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			number=data['number'],
			date=data['date'],
			file=file,
			series=series,
			cover=data['image'],
		)

		return i


	#==================================================================================================

	def _create_publisher(self, api_url, series_id):
		''' 
		Creates Publisher from ComicVine API URL and adds it to
		it's corresponding Series.

		Returns the Publisher object created.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.publisher_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		# Create Publisher
		p = Publisher.objects.create(
			cvid=data['cvid'],
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			logo=data['image'],
		)

		# Add Publisher to Series
		series = Series.objects.get(id=series_id)
		series.publisher = p
		series.save()

		return p


	#==================================================================================================

	def _create_team(self, api_url, issue_id):
		''' 
		Creates Team from ComicVine API URL and adds it to
		it's corresponding Issue.

		Returns the Team object created.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.team_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		issue = Issue.objects.get(id=issue_id)

		# Create Team
		t = issue.teams.create(
			cvid=data['cvid'],
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			image=data['image'],
		)

		# Add existing Characters to Team
		for character in response['results']['characters']:
			matching_character = Character.objects.filter(cvid=character['id'])
			if matching_character:
				team_item = Team.objects.filter(cvid=t.cvid)
				matching_character[0].teams.add(team_item[0])

		return t


	#==================================================================================================

	def _create_series(self, api_url):
		''' 
		Creates Series from ComicVine API URL.

		Returns the Series object created.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.series_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		# Create Series
		s = Series.objects.create(
			cvid=data['cvid'],
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			year=data['year'],
		)

		return s


	#==================================================================================================

	def _update_arc(self, obj_id, api_url):
		''' 
		Updates Arc from ComicVine API URL.

		Returns the Arc object udpated.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.arc_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		# Update Arc
		Arc.objects.filter(id=obj_id).update(
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			image=data['image'],
		)

		return Arc.objects.get(id=obj_id)


	#==================================================================================================

	def _update_character(self, obj_id, api_url):
		''' 
		Updates Character from ComicVine API URL.

		Returns the Character object udpated.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.character_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		# Update Character
		Character.objects.filter(id=obj_id).update(
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			image=data['image'],
		)

		return Character.objects.get(id=obj_id)


	#==================================================================================================

	def _update_creator(self, obj_id, api_url):
		''' 
		Updates Creator from ComicVine API URL.

		Returns the Creator object udpated.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.creator_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		# Update Creator
		Creator.objects.filter(id=obj_id).update(
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			image=data['image'],
		)

		return Creator.objects.get(id=obj_id)


	#==================================================================================================

	def _update_issue(self, obj_id, api_url, series_id):
		''' 
		Updates Issue from ComicVine API URL.

		Returns the Issue object udpated.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.issue_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		issue =Issue.objects.get(id=obj_id)
		self._reset_issue(issue.id)

		series = Series.objects.get(id=series_id)

		# Update Issue
		Issue.objects.filter(id=obj_id).update(
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			number=data['number'],
			date=data['date'],
			series=series,
			cover=data['image'],
		)

		return Issue.objects.get(id=obj_id)


	#==================================================================================================

	def _update_publisher(self, obj_id, api_url):
		''' 
		Updates Publisher from ComicVine API URL.

		Returns the Publisher object udpated.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.publisher_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		# Update Publisher
		Publisher.objects.filter(id=obj_id).update(
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			logo=data['image'],
		)

		return Publisher.objects.get(id=obj_id)


	#==================================================================================================

	def _update_team(self, obj_id, api_url):
		''' 
		Updates Team from ComicVine API URL.

		Returns the Team object udpated.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.team_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		# Update Team
		Team.objects.filter(id=obj_id).update(
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			image=data['image'],
		)

		return Team.objects.get(id=obj_id)


	#==================================================================================================

	def _update_series(self, obj_id, api_url):
		''' 
		Updates Series from ComicVine API URL.

		Returns the Series object udpated.
		'''

		# Request and Response
		request = Request(api_url + '?format=json&api_key=' + self._api_key + self.series_fields)
		response = json.loads(urlopen(request).read().decode('utf-8'))
		data = self._get_object_data(response['results'])

		# Update Series
		Series.objects.filter(id=obj_id).update(
			cvurl=data['cvurl'],
			name=data['name'],
			desc=data['desc'],
			year=data['year'],
		)

		return Series.objects.get(id=obj_id)

	#==================================================================================================

	def _reset_issue(self, obj_id):
		''' 
		Resets an Issue's fields.

		Returns the Issue object that was reset.
		'''
		issue = Issue.objects.get(id=obj_id)

		issue.cvurl = ''
		issue.name = ''
		issue.number = 1
		issue.date = datetime.date.today()
		issue.desc = ''
		issue.arcs.clear()
		issue.characters.clear()
		issue.creators.clear()
		issue.teams.clear()
		issue.cover = ''

		issue.save()

		return Issue.objects.get(id=obj_id)