from django import template
from django.conf import settings
from PIL import Image

register = template.Library()

@register.filter(name='smartcrop')
def smartcrop(value, arg):
	cache_url = ''

	if value:	
		# Get image
		img = Image.open(value)

		# Split width and height
		crop_size = arg.split('x')
		crop_width = int(crop_size[0])
		crop_height = int(crop_size[1])

		cache_url = ''

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
		cache_url = _save_image(value, cropped)

	return cache_url

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

def _save_image(filepath, image):

	filename = filepath.split('/')[-1]
	extension = '.' + filename.split('.')[1] if len(filename.split('.')) > 1 else '.jpg'
	cache = 'CACHE/' + filename.split('.')[0] + '-' + str(image.size[0]) + 'x' + str(image.size[1]) + extension
	image.save(settings.MEDIA_ROOT + '/' + cache)
	cache_url = settings.MEDIA_URL + cache

	return cache_url