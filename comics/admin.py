from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import Arc, Character, Creator, Team, Publisher, Series, Issue, Settings

admin.site.site_header = 'Tenma'
admin.site.site_title = 'Tenma'

admin.site.register(Settings, SingletonModelAdmin)
admin.site.register(Arc)
admin.site.register(Character)
admin.site.register(Creator)
admin.site.register(Team)
admin.site.register(Publisher)
admin.site.register(Series)
admin.site.register(Issue)