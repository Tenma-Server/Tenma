# README #

## What is this repository for? ##

Tenma is a comic server built on Django that allows you to store, organize, and read comics. It also leverages the [ComicVine API](http://comicvine.gamespot.com) to retrieve metadata on your comics. 

## How do I get set up? ##

Tenma is currently in alpha. Much of the instructions below will be automated so that setup is quick and painless.

This has been tested on Mac OSX 10.11 and Ubuntu 12.04.

#### Create the Virtual Environment ####

It is recommended to run Tenma in a Python Virtual Environment. 

1. Install Python 3.4 or greater: https://www.python.org/
2. Install Virtual Environment: `pip install virtualenv`
3. Change to the directory you want install Tenma.
4. Create your virtual environment: `virtualenv -p python3 venv`
5. Activate virtual environment: `source venv/bin/activate`

#### Install Tenma ####

6. Download the repository, unarchive it, and rename it to `tenmaserver`.
7. Copy `tenmaserver` to the `venv` directory.
8. Change into the `tenmaserver` directory.
9. Install dependencies: `pip install -r requirements.txt`

#### Create your database: ####

1. In the tenma root directory (`tenmaserver` in the example above), type `python manage.py migrate`
2. Create your user: `python manage.py createsuperuser`

#### Get running locally: ####

1. Then start your local server: `python manage.py runserver`
2. In your browser, go to `127.0.0.1:8000`

#### Getting your comics into the system: ####

1. Add your comics to the `tenmaserver/files` directory.
2. If you're using the ComicVine API:
	1. In Tenma, click the Settings button in the top-right corner.
	2. Enter in your ComicVine API Key, and click "Save".
3. In Tenma, click the settings button in the top-right corner.
4. Click the "Import Comics" button.
5. Wait for the page to reload, and your comics will be showing. If you're using the ComicVine API, this can take some time. The more metadata gathered, the faster it will be over time.

## Supported filetypes ##

* CBZ
* ZIP
* CBR
* RAR
* CBT
* TAR