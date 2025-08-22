from rest_framework.test import APITestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.conf import settings
from PIL import Image
from unittest.mock import patch
import io
import os
import tempfile

from remover.views import RemoveBackgroundView
from remover.serializers import ImageUploadSerializer


def make_png_bytes(mode="RGBA", size=(100, 100), color=(0, 0, 0, 255)):
    img = Image.new(mode, size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class RemoveBackgroundAPITest(APITestCase):
    def setUp(self):
        self.url = reverse("remove-background")
        self.patch_target = f"{RemoveBackgroundView.__module__}.remove"

    def _fresh_image_file(self, name="test.png"):
        data = make_png_bytes(mode="RGBA", size=(100, 100), color=(0, 0, 0, 255))
        return SimpleUploadedFile(name, data, content_type="image/png")

    def test_remove_background_success(self):
        transparent_png = make_png_bytes(
            mode="RGBA", size=(100, 100), color=(0, 0, 0, 0)
        )
        with patch(self.patch_target, autospec=True) as mock_remove:
            mock_remove.return_value = transparent_png
            img = self._fresh_image_file()
            resp = self.client.post(self.url, {"image": img}, format="multipart")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "image/png")
        self.assertTrue(resp.content)

        out = Image.open(io.BytesIO(resp.content))
        self.assertIn(out.mode, ("RGBA", "LA"))
        alpha = out.getchannel("A")
        min_a, _ = alpha.getextrema()
        self.assertLess(min_a, 255)

    def test_missing_image_returns_400(self):
        resp = self.client.post(self.url, {}, format="multipart")
        self.assertEqual(resp.status_code, 400)

    def test_invalid_file_returns_400(self):
        bad = SimpleUploadedFile(
            "not_image.txt", b"not an image", content_type="text/plain"
        )
        resp = self.client.post(self.url, {"image": bad}, format="multipart")
        self.assertEqual(resp.status_code, 400)

    def test_get_not_allowed(self):
        resp = self.client.get(self.url)
        self.assertIn(resp.status_code, (404, 405))

    def test_internal_error_returns_500(self):
        with patch(self.patch_target, side_effect=Exception("boom"), autospec=True):
            img = self._fresh_image_file()
            resp = self.client.post(self.url, {"image": img}, format="multipart")
        self.assertEqual(resp.status_code, 500)
        self.assertIn("Failed to process image", resp.data.get("error", ""))

    def test_endpoint_does_not_write_to_disk(self):
        with patch(self.patch_target, autospec=True) as mock_remove:
            mock_remove.return_value = make_png_bytes(
                mode="RGBA", size=(10, 10), color=(0, 0, 0, 0)
            )
            media_root = os.path.abspath(settings.MEDIA_ROOT)
            before = set(os.listdir(media_root))
            img = self._fresh_image_file()
            _ = self.client.post(self.url, {"image": img}, format="multipart")
            after = set(os.listdir(media_root))
        self.assertEqual(before, after)

    def test_large_file_returns_400(self):
        base = make_png_bytes(mode="RGBA", size=(200, 200), color=(0, 0, 0, 255))
        pad = b"0" * (ImageUploadSerializer.MAX_UPLOAD_SIZE + 1)
        big_bytes = base + pad
        big_file = SimpleUploadedFile("big.png", big_bytes, content_type="image/png")
        resp = self.client.post(self.url, {"image": big_file}, format="multipart")
        self.assertEqual(resp.status_code, 400)
