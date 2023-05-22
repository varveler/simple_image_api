from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .models import Image, TempImageFile
from .serializers import ImageSerializer, EditTitleImageSerializer
from .tasks import handle_image_processing


class ImageList(APIView, LimitOffsetPagination):
    """
    List images, or create a new image.
    """
    def get(self, request, format=None):
        images = Image.objects.all()
        title = request.query_params.get('search', None)
        if title is not None:
            images = images.filter(title__icontains=title)
        # Apply pagination
        paginated_images = self.paginate_queryset(images, request)
        serializer = ImageSerializer(paginated_images, many=True)
        return self.get_paginated_response(serializer.data)

    def perform_create(self, serializer):
        image = serializer.validated_data.get('image')
        title = serializer.validated_data.get('title')
        height = serializer.validated_data.get('height')
        width = serializer.validated_data.get('width')
        obj = TempImageFile.objects.create(temp_file=image)
        title = title if title else obj.original_filename
        handle_image_processing.delay(obj.id, title, width, height)

    def post(self, request, format=None):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({'message':'OK', 'result': 'processing image'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageDetail(APIView):
    """
    Retrieve an image details by id
    """ 
    def get_object(self, pk):
        try:
            return Image.objects.get(pk=pk)
        except Image.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        image = self.get_object(pk)
        serializer = ImageSerializer(image)
        return Response(serializer.data)
    
    def put(self, request, pk):
        image = self.get_object(pk)
        serializer = EditTitleImageSerializer(image, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            response_serilizer = ImageSerializer(obj) # to return the whole object
            return Response(response_serilizer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        image = self.get_object(pk)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

    