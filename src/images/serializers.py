from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'title', 'width', 'height', 'url', 'image']
    
    # to return a parameter named 'url' we create a method field:
    url = serializers.SerializerMethodField('get_url', read_only=True)
    width = serializers.IntegerField(min_value=1, max_value=400)
    height = serializers.IntegerField(min_value=1, max_value=400)

    def get_url(self, obj):
        return obj.image.url


class EditTitleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['title']