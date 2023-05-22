from celery import shared_task
from django.core.files import File

from .models import TempImageFile, Image
from .services import optimize_image, resize_image


@shared_task()
def handle_image_processing(image_id, title, width, height):
    temp_image = TempImageFile.objects.get(id=image_id)
    path = temp_image.temp_file.path
    optimize_image(path)
    resize_image(path, width, height)
    obj = Image.objects.create(title=title,
                               width=width,
                               height=height,
                               image=File(temp_image.temp_file, 
                                          temp_image.temp_file.name))
    temp_image.delete()
    return f'image object was saved with url {obj.image.url} '
