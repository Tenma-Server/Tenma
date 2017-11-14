from __future__ import absolute_import
from celery.decorators import task
from .utils.comicimporter import ComicImporter

@task(name="import_comic_files_task")
def import_comic_files_task():
	importer = ComicImporter()
	importer.import_comic_files()

@task(name="reprocess_issue_task")
def reprocess_issue_task(slug):
	comicimporter = ComicImporter()
	comicimporter.reprocess_issue(slug)
