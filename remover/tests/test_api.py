from rest_framework.test import APITestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

class RemoveBackgroundAPITest(APITestCase):
    def setUp(self):
        # Create a simple black square image in memory
        image = Image.new('RGB', (100, 100), color='black')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        self.test_image = SimpleUploadedFile(
            "test.png", buffer.read(), content_type="image/png"
        )

    def test_remove_background_success(self):
        url = reverse('remove-background')
        response = self.client.post(url, {'image': self.test_image}, format='multipart')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
