from urllib.request import urlretrieve, urlopen, Request
from urllib.parse import quote_plus, unquote_plus
from comics.models import Arc, Character, Creator, Team, Publisher, Series, Issue
from . import fnameparser
import json, os, time

class CVScraper(object):

	#==================================================================================================

	def __init__(self):
		self._api_key = 'd1fe390344414d5bfdd36060fd8f7e3efa074c19'
		self.directory_path = 'files/'

	#==================================================================================================

	def process_issues(self):
		# Settings for comics directory
		processed_files_file = self.directory_path + '.processed'

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
						if file.endswith(".cbz") or file.endswith(".zip") or file.endswith(".cbr") or file.endswith(".rar") or file.endswith(".cbt") or file.endswith(".tar"): 
							# Attempt to find match
							cvid = self._find_match(file)

							if not cvid == '':
								# Scrape the issue
								self._scrape_issue(file, cvid)
								# Write to the .processed file
								pff.write("%s\n" % file)

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
			cvid = self._find_match_with_series(matching_series[0].cvid, issue_number)
			return cvid

		# Attempt to find issue based on extracted Series Name and Issue Number
		query_url = 'http://comicvine.gamespot.com/api/search?format=json&resources=issue' + '&api_key=' + self._api_key + query_fields + query_limit + '&query='

		# Check for series name and issue number, or just series name
		if series_name and issue_number:
			query_url = query_url + series_name_url + '%20%23' + issue_number
			query_request = Request(query_url)
			query_response = json.loads(urlopen(query_request).read())
		elif series_name:
			query_url = query_url + series_name_url
			query_request = Request(query_url)
			query_response = json.loads(urlopen(query_request).read())

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
			elif series_name and issue_year:
				if item_name == series_name and item_year == issue_year:
					best_option_list.append(issue['id'])
			elif series_name:
				if item_name == series_name and item_number == '1':
					best_option_list.append(issue['id'])

		return best_option_list[0] if best_option_list else ''

	#==================================================================================================

	def _find_match_with_series(self, series_cvid, issue_number):

		# Initialize response
		cvid = series_cvid

		# Query Settings
		query_fields = '&field_list=issues'

		# Attempt to find issue based on extracted Series Name and Issue Number
		query_request = Request('http://comicvine.gamespot.com/api/volume/4050-' + cvid + '?format=json&api_key=' + self._api_key + query_fields)
		query_response = json.loads(urlopen(query_request).read())

		# Try to find the closest match.
		for issue in query_response['results']['issues']:
			item_number = issue['issue_number'] if issue['issue_number'] else ''

			if issue_number:
				if item_number == issue_number:
					issue_cvid = issue['id']

		return issue_cvid

	#==================================================================================================

	def _scrape_issue(self, filename, cvid):
		# Set fields to grab when calling the API.
		# This helps increase performance per call.
		arc_fields = '&field_list=deck,description,id,image,name,site_detail_url'
		character_fields = '&field_list=deck,description,id,image,name,site_detail_url'
		creator_fields = '&field_list=deck,description,id,image,name,site_detail_url'
		team_fields = '&field_list=characters,deck,description,id,image,name,site_detail_url'
		publisher_fields = '&field_list=deck,description,id,image,name,site_detail_url'
		series_fields = '&field_list=deck,description,id,name,publisher,site_detail_url,start_year'
		issue_fields = '&field_list=character_credits,cover_date,deck,description,id,image,issue_number,name,person_credits,site_detail_url,story_arc_credits,team_credits,volume'

		# Make API call and store issue response
		request_issue = Request('http://comicvine.gamespot.com/api/issue/4000-' + str(cvid) + '/?format=json&api_key=' + self._api_key + issue_fields)
		response_issue = json.loads(urlopen(request_issue).read())
		time.sleep(1)

		# 1. Set basic issue information:
		issue = Issue()
		issue.file = self.directory_path + filename
		issue.cvid = response_issue['results']['id']
		issue.cvurl = response_issue['results']['site_detail_url']
		issue.name = response_issue['results']['name'] if response_issue['results']['name'] else ''
		issue.number = response_issue['results']['issue_number']
		issue.date = response_issue['results']['cover_date']

		if response_issue['results']['deck']:
			issue.desc = response_issue['results']['deck']
		elif response_issue['results']['description']:
			issue.desc = response_issue['results']['description']
		else:
			issue.desc = ''

		issue_cover_url = response_issue['results']['image']['super_url']
		issue_cover_filename = unquote_plus(issue_cover_url.split('/')[-1])
		issue.cover = urlretrieve(issue_cover_url, 'media/images/covers/' + issue_cover_filename)[0]

		# 2. Set Series info:
		matching_series = Series.objects.filter(cvid=response_issue['results']['volume']['id'])

		if not matching_series:
			series = Series()

			request_series = Request(response_issue['results']['volume']['api_detail_url'] + '?format=json&api_key=' + self._api_key + series_fields)
			response_series = json.loads(urlopen(request_series).read())
			time.sleep(1)

			series.cvid = response_series['results']['id']
			series.cvurl = response_series['results']['site_detail_url']
			series.name = response_series['results']['name']

			if response_series['results']['deck']:
				series.desc = response_series['results']['deck']
			elif response_series['results']['description']:
				series.desc = response_series['results']['description']
			else:
				series.desc = ''

			# 3. Set Publisher info:
			matching_publisher = Publisher.objects.filter(cvid=response_series['results']['publisher']['id'])

			if not matching_publisher:
				publisher = Publisher()

				# Store publisher response
				request_publisher = Request(response_series['results']['publisher']['api_detail_url'] + '?format=json&api_key=' + self._api_key + publisher_fields)
				response_publisher = json.loads(urlopen(request_publisher).read())
				time.sleep(1)

				if response_publisher['results']['image']:
					publisher_logo_url = response_publisher['results']['image']['super_url']
					publisher_logo_filename = unquote_plus(publisher_logo_url.split('/')[-1])
					publisher_logo_filepath = urlretrieve(publisher_logo_url, 'media/images/publishers/' + publisher_logo_filename)[0]
				else:
					publisher_logo_filepath = ''

				publisher.cvid = response_publisher['results']['id']
				publisher.cvurl = response_publisher['results']['site_detail_url']
				publisher.name = response_publisher['results']['name']

				if response_publisher['results']['deck']:
					publisher.desc = response_publisher['results']['deck']
				elif response_publisher['results']['description']:
					publisher.desc = response_publisher['results']['description']
				else:
					publisher.desc = ''

				publisher.logo = publisher_logo_filepath

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
				request_arc = Request(story_arc['api_detail_url'] + '?format=json&api_key=' + self._api_key + arc_fields)
				response_arc = json.loads(urlopen(request_arc).read())

				# Get Arc image
				if response_arc['results']['image']:
					arc_image_url = response_arc['results']['image']['super_url']
					arc_image_filename = unquote_plus(arc_image_url.split('/')[-1])
					arc_image_filepath = urlretrieve(arc_image_url, 'media/images/arcs/' + arc_image_filename)[0]
				else:
					arc_image_filepath = ''

				if response_arc['results']['deck']:
					arc_desc = response_arc['results']['deck']
				elif response_arc['results']['description']:
					arc_desc = response_arc['results']['description']
				else:
					arc_desc = ''

				# Create Arc
				issue.arcs.create(
					cvid=response_arc['results']['id'],
					cvurl=response_arc['results']['site_detail_url'],
					name=response_arc['results']['name'],
					desc=arc_desc,
					image=arc_image_filepath
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
				request_character = Request(character['api_detail_url'] + '?format=json&api_key=' + self._api_key + character_fields)
				response_character = json.loads(urlopen(request_character).read())

				# Get character image
				if response_character['results']['image']:
					character_image_url = response_character['results']['image']['super_url']
					character_image_filename = unquote_plus(character_image_url.split('/')[-1])
					character_image_filepath = urlretrieve(character_image_url, 'media/images/characters/' + character_image_filename)[0]
				else:
					character_image_filepath = ''

				if response_character['results']['deck']:
					character_desc = response_character['results']['deck']
				elif response_character['results']['description']:
					character_desc = response_character['results']['description']
				else:
					character_desc = ''

				# Create Character
				issue.characters.create(
					cvid=response_character['results']['id'],
					cvurl=response_character['results']['site_detail_url'],
					name=response_character['results']['name'],
					desc=character_desc,
					image=character_image_filepath
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
				# Store Character response
				request_creator = Request(person['api_detail_url'] + '?format=json&api_key=' + self._api_key + creator_fields)
				response_creator = json.loads(urlopen(request_creator).read())

				# Get character image
				if response_creator['results']['image']:
					creator_image_url = response_creator['results']['image']['super_url']
					creator_image_filename = unquote_plus(creator_image_url.split('/')[-1])
					creator_image_filepath = urlretrieve(creator_image_url, 'media/images/creators/' + creator_image_filename)[0]
				else:
					creator_image_filepath = ''

				if response_creator['results']['deck']:
					creator_desc = response_creator['results']['deck']
				elif response_creator['results']['description']:
					creator_desc = response_creator['results']['description']
				else:
					creator_desc = ''

				# Create Character
				issue.creators.create(
					cvid=response_creator['results']['id'],
					cvurl=response_creator['results']['site_detail_url'],
					name=response_creator['results']['name'],
					desc=creator_desc,
					image=creator_image_filepath
				)

			else:
				# Add found Character to Issue
				issue.creators.add(matching_creator[0])

		# 8. Set Teams info
		for team in response_issue['results']['team_credits']:
			time.sleep(1)

			matching_team = Team.objects.filter(cvid=team['id'])

			if not matching_team:
				request_team = Request(team['api_detail_url'] + '?format=json&api_key=' + self._api_key + team_fields)
				response_team = json.loads(urlopen(request_team).read())

				if response_team['results']['image']:
					team_image_url = response_team['results']['image']['super_url']
					team_image_filename = unquote_plus(team_image_url.split('/')[-1])
					team_image_filepath = urlretrieve(team_image_url, 'media/images/teams/' + team_image_filename)[0]
				else:
					team_image_filepath = ''

				if response_team['results']['deck']:
					team_desc = response_team['results']['deck']
				elif response_team['results']['description']:
					team_desc = response_team['results']['description']
				else:
					team_desc = ''

				issue.teams.create(
					cvid=response_team['results']['id'],
					cvurl=response_team['results']['site_detail_url'],
					name=response_team['results']['name'],
					desc=team_desc,
					image=team_image_filepath
				)

				for character in response_team['results']['characters']:
					matching_character = Character.objects.filter(cvid=character['id'])
					if matching_character:
						team_item = Team.objects.filter(cvid=team['id'])
						matching_character[0].teams.add(team_item[0])

			else:
				issue.teams.add(matching_team[0])