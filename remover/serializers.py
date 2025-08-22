from django.conf import settings
from rest_framework import serializers


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
    MAX_UPLOAD_SIZE = getattr(settings, "MAX_UPLOAD_SIZE", 5 * 1024 * 1024)

    def validate_image(self, file):
        size = getattr(file, "size", None)
        if size is not None and size > self.MAX_UPLOAD_SIZE:
            mb = self.MAX_UPLOAD_SIZE // (1024 * 1024)
            raise serializers.ValidationError(
                f"Image too large. Maximum allowed size is {mb} MB."
            )
        return file
