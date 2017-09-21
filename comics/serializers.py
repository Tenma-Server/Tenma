from django.contrib.auth.models import User, Group
from .models import Series, Issue, Character, Arc, Team, Publisher, Creator, Settings
from rest_framework import serializers

class ArcSerializer(serializers.HyperlinkedModelSerializer):
	issues = serializers.HyperlinkedRelatedField(many=True, view_name='issue-detail', read_only=True)

	class Meta:
		model = Arc
		fields = (
					'url',
					'id',
					'cvid',
					'cvurl',
					'name',
					'desc',
					'image',
					'issues',
				 )

class CharacterSerializer(serializers.HyperlinkedModelSerializer):
	issues = serializers.HyperlinkedRelatedField(many=True, view_name='issue-detail', read_only=True)
	teams = serializers.HyperlinkedRelatedField(many=True, view_name='team-detail', read_only=True)

	class Meta:
		model = Character
		fields = (
					'url',
					'id',
					'cvid',
					'cvurl',
					'name',
					'desc',
					'image',
					'teams',
					'issues',
				 )

class CreatorSerializer(serializers.HyperlinkedModelSerializer):
	issues = serializers.HyperlinkedRelatedField(many=True, view_name='issue-detail', read_only=True)

	class Meta:
		model = Creator
		fields = (
					'url',
					'id',
					'cvid',
					'cvurl',
					'name',
					'desc',
					'image',
					'issues',
				 )

class GroupSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Group
		fields = (
					'url',
					'name',
				 )

class IssueSerializer(serializers.HyperlinkedModelSerializer):
	arcs = serializers.HyperlinkedRelatedField(many=True, view_name='arc-detail', read_only=True)
	series = serializers.HyperlinkedRelatedField(view_name='series-detail', read_only=True)
	characters = serializers.HyperlinkedRelatedField(many=True, view_name='character-detail', read_only=True)
	creators = serializers.HyperlinkedRelatedField(many=True, view_name='creator-detail', read_only=True)
	teams = serializers.HyperlinkedRelatedField(many=True, view_name='team-detail', read_only=True)

	class Meta:
		model = Issue
		fields = (
					'url',
					'id',
					'cvid',
					'cvurl',
					'series',
					'name',
					'number',
					'date',
					'desc',
					'arcs',
					'characters',
					'creators',
					'teams',
					'file',
					'image',
				 )

class PublisherSerializer(serializers.HyperlinkedModelSerializer):
	series = serializers.HyperlinkedRelatedField(many=True, view_name='series-detail', read_only=True)

	class Meta:
		model = Publisher
		fields = (
					'url',
					'id',
					'cvid',
					'cvurl',
					'name',
					'desc',
					'logo',
					'series',
				 )

class SeriesSerializer(serializers.HyperlinkedModelSerializer):
	issues = serializers.HyperlinkedRelatedField(many=True, view_name='issue-detail', read_only=True)
	publisher = serializers.HyperlinkedRelatedField(view_name='publisher-detail', read_only=True)
	image = serializers.ReadOnlyField()

	class Meta:
		model = Series
		fields = (
					'url',
					'id',
					'cvid',
					'cvurl',
					'name',
					'publisher',
					'year',
					'desc',
					'issues',
					'image',
				 )

class SettingsSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Settings
		fields = ('__all__')

class TeamSerializer(serializers.HyperlinkedModelSerializer):
	characters = serializers.HyperlinkedRelatedField(many=True, view_name="character-detail", read_only=True)
	issues = serializers.HyperlinkedRelatedField(many=True, view_name='issue-detail', read_only=True)

	class Meta:
		model = Team
		fields = (
					'url',
					'id',
					'cvid',
					'cvurl',
					'name',
					'desc',
					'image',
					'characters',
					'issues',
				 )

class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = (
					'url',
					'username',
					'email',
					'groups',
				 )
