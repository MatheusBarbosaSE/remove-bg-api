from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ImageUploadSerializer

from rembg import remove
from PIL import Image, UnidentifiedImageError
import io
from django.http import HttpResponse


class RemoveBackgroundView(APIView):
    def post(self, request, format=None):
        serializer = ImageUploadSerializer(data=request.data)

        if serializer.is_valid():
            image_file = serializer.validated_data["image"]

            try:
                input_image = Image.open(image_file)

                image_format = input_image.format if input_image.format else "PNG"

                image_bytes = io.BytesIO()
                input_image.save(image_bytes, format=image_format)
                image_bytes = image_bytes.getvalue()

                output_bytes = remove(image_bytes)

                return HttpResponse(output_bytes, content_type="image/png")

            except UnidentifiedImageError:
                return Response(
                    {"error": "The uploaded file is not a valid image."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"error": "Failed to process image.", "details": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
