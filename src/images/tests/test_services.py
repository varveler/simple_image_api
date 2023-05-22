import os

from PIL import Image
from django.test import TestCase

from images.services import optimize_image, resize_image

class ImageServicesTestCase(TestCase):

    def generate_image(self, width, height, color, path):
        """Generates a regular image of the provided color 
           and saves it to the provided path"""
        img = Image.new('RGB', (width, height), color)
        img.save(path)

    def setUp(self):
        self.image_path = 'images/tests/test.png'
        self.generate_image(300, 300, 'red', self.image_path)

    def tearDown(self):
        os.remove(self.image_path)

    def test_optimize_image(self):
        original_size = os.path.getsize(self.image_path)
        optimize_image(self.image_path)
        optimized_size = os.path.getsize(self.image_path)
        self.assertLess(optimized_size, original_size, 'Image not optimized')

    def test_resize_image(self):
        width, height = 100, 100
        resize_image(self.image_path, width, height)
        with Image.open(self.image_path) as image:
            self.assertEqual(image.size, (width, height))  
