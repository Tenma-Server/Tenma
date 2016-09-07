import datetime
from django.test import TestCase
from ..models import Arc, Character, Creator, Issue, Publisher, Series, Team

class ArcTest(TestCase):
	def create_arc(self, name="Another Civil War"):
		return Arc.objects.create(name=name)

	def test_arc_creation(self):
		a = self.create_arc()
		self.assertTrue(isinstance(a, Arc))
		self.assertEqual(a.__str__(), a.name)

class CharacterTest(TestCase):
	def create_character(self, name="The Super Guy"):
		return Character.objects.create(name=name)

	def test_character_creation(self):
		c = self.create_character()
		self.assertTrue(isinstance(c, Character))
		self.assertEqual(c.__str__(), c.name)

class CreatorTest(TestCase):
	def create_creator(self, name="The Illustrator"):
		return Creator.objects.create(name=name)

	def test_creator_creation(self):
		c = self.create_creator()
		self.assertTrue(isinstance(c, Creator))
		self.assertEqual(c.__str__(), c.name)

class IssueTest(TestCase):
	def create_issue(self, name="The First Issue", number=1):
		series = SeriesTest.create_series(self)
		return Issue.objects.create(name=name, number=number, date=datetime.date.today(), series=series)

	def test_issue_creation(self):
		i = self.create_issue()
		self.assertTrue(isinstance(i, Issue))
		self.assertEqual(i.__str__(), i.name)
		self.assertEqual(i.number, 1)
		self.assertEqual(i.date, datetime.date.today())
		self.assertTrue(isinstance(i.series, Series))

class PublisherTest(TestCase):
	def create_publisher(self, name="That Comic Publisher"):
		return Publisher.objects.create(name=name)

	def test_publisher_creation(self):
		p = self.create_publisher()
		self.assertTrue(isinstance(p, Publisher))
		self.assertEqual(p.__str__(), p.name)

class SeriesTest(TestCase):
	def create_series(self, name="Long Series"):
		return Series.objects.create(name=name)

	def test_series_creation(self):
		s = self.create_series()
		self.assertTrue(isinstance(s, Series))
		self.assertEqual(s.__str__(), s.name)

class TeamTest(TestCase):
	def create_team(self, name="The Greatest Team"):
		return Team.objects.create(name=name)

	def test_team_creation(self):
		t = self.create_team()
		self.assertTrue(isinstance(t, Team))
		self.assertEqual(t.__str__(), t.name)