import os

from django import template
from django.conf import settings
from PIL import Image

register = template.Library()

@register.filter(name='smartcrop')
def smartcrop(value, arg):
	cache_url = ''

	if value:

		# Split width and height
		crop_size = arg.split('x')
		crop_width = int(crop_size[0])
		crop_height = int(crop_size[1])

		cache_paths = _create_cache_paths(value, crop_width, crop_height)

		if os.path.isfile(cache_paths[0]):
			return cache_paths[1]
		else:
			# Get image
			img = Image.open(value)

			# Check Aspect ratio and resize acordingly
			if crop_width * img.height < crop_height * img.width:
				height_percent = (float(crop_height)/float(img.size[1]))
				width_size = int(float(img.size[0])*float(height_percent))
				img = img.resize((width_size,crop_height), Image.BICUBIC)

			else:
				width_percent = (float(crop_width)/float(img.size[0]))
				height_size = int(float(img.size[1])*float(width_percent))
				img = img.resize((crop_width,height_size), Image.BICUBIC)

			cropped = _crop_from_center(img, crop_width, crop_height)
			cropped.save(cache_paths[0])

	return cache_paths[1]

def _crop_from_center(image, width, height):

	img = image

	center_width = img.size[0] / 2
	center_height = img.size[1] / 2

	cropped = img.crop(
		(
			center_width - width / 2,
			center_height - height / 2,
			center_width + width / 2,
			center_height + height / 2 
		)
	)

	return cropped

def _create_cache_paths(filepath, width, height):
	filename = filepath.split('/')[-1]
	extension = os.path.splitext(filename)[1].lower() if os.path.splitext(filename)[1] else '.jpg'
	cache = 'CACHE/' + filename.split('.')[0] + '-' + str(width) + 'x' + str(height) + extension
	cache_static = settings.MEDIA_ROOT + '/' + cache
	cache_url = settings.MEDIA_URL + cache

	return (cache_static, cache_url)