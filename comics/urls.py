from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from comics.views import index

app_name = 'comics'
urlpatterns = [
	url(r'^$', index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
