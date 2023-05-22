import os
import io

from PIL import Image as PILImage
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIRequestFactory

from image_api.celery import app as celery_app
from images.models import Image
from images.views import ImageList, ImageDetail


class ImageListTestCase(APITestCase):
    def setUp(self):
        # to tasks to run synchronously:
        celery_app.conf.update(CELERY_ALWAYS_EAGER=True)
        self.factory = APIRequestFactory()
        self.view = ImageList.as_view()
        self.uri = '/images/'
        self.file_name = 'MyTestImageToBeDeleted'
        self.store_folder = os.path.join(settings.MEDIA_ROOT, 'tempImageFiles')
        self.image = Image.objects.create(title='Test Image', width=100, height=100, image="test.jpg")
        # override S3 storage on field image with Local Storage for testing
        self.image_field = Image._meta.get_field('image')
        self.default_storage = self.image_field.storage
        self.image_field.storage = FileSystemStorage()
        

    def tearDown(self):
        celery_app.conf.update(CELERY_ALWAYS_EAGER=False)
        self.image_field.storage = self.default_storage
        # remove all created images files
        test_images = [f for f in os.listdir(self.store_folder) if f.startswith(self.file_name)]
        for img in test_images:
            os.remove(os.path.join(self.store_folder, img))
        
    def test_list(self):
        request = self.factory.get(self.uri)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)

    def test_response_is_paginated(self):
        for i in range(15):
            Image.objects.create(title="Test Image", 
                                image="test.jpg",
                                width=100, 
                                height=100)
        response = self.client.get('/images/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('next' in response.data)
        self.assertTrue('count' in response.data)
        self.assertTrue('previous' in response.data)

    def test_search(self):
        request = self.factory.get(self.uri, {'search': 'Test Image'})
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Image')

    def test_post_no_image(self):
        request = self.factory.post(self.uri, {'title': 'New Image', 'width': 100, 'height': 100})
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"image":["No file was submitted."]}')

    def test_create(self):
        img_file = io.BytesIO()
        image = PILImage.new('RGB', (100, 100), 'red')
        image.save(img_file, format='png')
        img_file.seek(0)
        upload = SimpleUploadedFile(f'{self.file_name}.png', 
                                    img_file.read(), 
                                    content_type='image/png')
        data = {
            'image': upload,
            'height': 50,
            'width': 50,
            'title': 'MyRedImage'
        }

        response = self.client.post(self.uri, data, format='multipart')
        response.render()
        self.assertEqual(response.status_code, 200)
        image = Image.objects.get(title='MyRedImage')
        self.assertIsNotNone(image.image)


class ImageDetailTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ImageDetail.as_view()
        self.image = Image.objects.create(title='Test Image',
                                          width=100,
                                          height=100,
                                          image="test.jpg")
        self.uri = f'/images/{self.image.pk}/'

    def test_detail(self):
        request = self.factory.get(self.uri)
        response = self.view(request, pk=self.image.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Image')
        self.assertTrue('id' in response.data)
        self.assertTrue('url' in response.data)
        self.assertTrue('title' in response.data)
        self.assertTrue('width' in response.data)
        self.assertTrue('height' in response.data)



