# README #

Tenma is a comic server based on Django. This is highly beta right now, and needs a lot of work. Much of the below will be automated so that setup is quick and painless. 

### What is this repository for? ###

Storing, organizing, and reading comics.

### How do I get set up? ###

Dependencies:
1. Install python
2. Install Django: https://www.djangoproject.com/download/
3. Install the rarfile python library: https://pypi.python.org/pypi/rarfile/2.2

Create your database:
1. In the tenma root directory, type `python manage.py migrate`
2. Create your user: `python manage.py createsuperuser`

Get running:
1. Then start your local server: python manage.py runserver
2. Access from 127.0.0.1:8000

Get your comics into the system:
1. Add your comics to the tenma/files directory (if it doesn't exist, create it)
2. Go to 127.0.0.1:8000/testing_cvscraper
3. Once the page is loaded, go to 127.0.0.1:8000 and your comics will be loaded!

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact