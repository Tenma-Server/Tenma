# README #

Tenma is a comic server based on Django. This is highly beta right now, and needs a lot of work. Much of the below will be automated so that setup is quick and painless. 

## What is this repository for? ##

Storing, organizing, and reading comics.

## How do I get set up? ##

So far this has been tested only in a Mac environment. Theoretically it should work fine in a Linux environment as well.

### Virtual Environment ###

It is recommended to run Tenma in a Python Virtual Environment. 

1. Install Python 3.4 or greater
2. In Terminal, run `pip install virtualenv`
3. Change to the directory you want install Tenma.
3. Create virtual environment: `virtualenv -p python3 tenma`
4. Activate virtual environment: `source tenma/bin/activate`
5. Copy the Tenma files to a directory in the virtualenv.
6. Install dependencies.

### Dependencies: ###

1. Install Django: `pip install django`
2. Install the rarfile python library: `pip install rarfile`
3. Install Pillow: `pip install Pillow`

### Create your database: ###

1. In the tenma root directory, type `python manage.py migrate`
2. Create your user: `python manage.py createsuperuser`

### Get running: ###

1. Then start your local server: python manage.py runserver
2. Access from 127.0.0.1:8000

### Get your comics into the system: ###

1. Add your comics to the tenma/files directory (if it doesn't exist, create it)
2. In Tenma, click the "Import Comics" button in the top-right corner.
3. Wait for the page to reload, and your comics will show.

## Supported filetypes ##

* CBZ
* ZIP
* CBR
* RAR
* CBT
* TAR