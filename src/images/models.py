from django.db import models
from custom_storage import S3ImageStorage
import os 


class TempImageFile(models.Model):
    temp_file = models.ImageField(upload_to='tempImageFiles')

    @property
    def filename(self):
        return os.path.basename(self.temp_file.path)

    @property
    def original_filename(self):
        file_name = os.path.basename(self.temp_file.path)
        return os.path.splitext(file_name)[0]

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.temp_file.path):
            os.remove(self.temp_file.path)
        super(TempImageFile, self).delete(*args,**kwargs)


class Image(models.Model):
    title = models.CharField(max_length=200, blank=True)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    image = models.ImageField(storage=S3ImageStorage(),  max_length=500)