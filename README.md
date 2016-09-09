# Tenma #

**Tenma is currently in alpha. I can not claim that this application is secure to run over the internet.**

Tenma is a comic server built on Django that allows you to store, organize, and read comics. It focuses heavily on creating relationships between issues spanning different series based on Characters, Creators, Teams, Story Arcs and Publishers. To do this, it leverages the [ComicVine](http://comicvine.gamespot.com) [API](http://comicvine.gamespot.com/api) to retrieve metadata on your comics (ComicVine account required). 

## Installation and Configuration ##

In the future, much of the instructions below will be automated so that setup is quick and painless. 

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

1. Then start your local server: `python manage.py runserver [YOUR IP ADDRESS]:8000`
	* For example: `python manage.py runserver 192.168.1.30:8000`
2. In your browser, go to `[YOUR IP ADDRESS]:8000`
	* For example: `http://192.168.1.30:8000` 

#### Getting your comics into the system: ####

1. Add your comics to the `tenmaserver/files` directory.
2. If you're using the ComicVine API:
	1. In Tenma, click the Settings button in the top-right corner.
	2. Enter in your ComicVine API Key, and click "Save".
3. In Tenma, click the settings button in the top-right corner.
4. Click the "Import Comics" button.
5. Wait for the page to reload, and your comics will be showing. If you're using the ComicVine API, this can take some time. The more metadata gathered, the faster it will be over time.

#### Current supported filetypes ####

* CBZ
* ZIP
* CBR
* RAR
* CBT
* TAR

## Using The Reader ##

#### Reading ####
To read a comic click the comic image on an issue page. 

#### Navigating ####
To navigate, you can use the arrow buttons, or your keyboard arrows.

#### View Modes ####
From the top menu (visible when you move your mouse), you can change the view mode from fit horizontally to fit vertically.

# Screenshots #

![homepage](./screenshots/issue.png)
*For more screenshots, check out the screenshots directory*

# Contributing #
Since this is my first Django project, I appreciate any contributions to Tenma.
