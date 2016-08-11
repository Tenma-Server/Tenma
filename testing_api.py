from urllib2 import Request, urlopen

import json

# Store API key
api_key = 'd1fe390344414d5bfdd36060fd8f7e3efa074c19'

# Make API call and store volume response
request = Request('http://comicvine.gamespot.com/api/volume/4050-18253/?format=json&api_key=' + api_key)
volume = json.loads(urlopen(request).read())

# Parse volume name and id
volume_name = volume['results']['name']
volume_id = str(volume['results']['id'])
print 'Name: ' + volume_name
print 'ID: ' + volume_id

# Test issues
volume_issues = volume['results']['issues']
print volume_issues
