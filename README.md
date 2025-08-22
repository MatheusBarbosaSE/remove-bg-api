# Background Remover API

A **Django REST API** for removing image backgrounds using the [`rembg`](https://github.com/danielgatis/rembg) library.  
This project processes images **in-memory** and returns the result as a **transparent PNG**.  
It does **not store images on disk**, making it **fast and secure**.

---

## 🚀 Features
- Remove image background with **rembg**
- RESTful API with **Django REST Framework**
- **No file storage** – returns processed image directly
- Ready for **local development** and **integration** into other projects
- Supports **CORS for local testing**

---

## 📦 Requirements
- **Python 3.10+**
- Virtual environment (recommended)
- Dependencies listed in `requirements.txt`:

  ```txt
  Django==5.2.4
  djangorestframework==3.16.0
  django-cors-headers==4.7.0
  rembg==2.0.67
  onnxruntime==1.22.1
  pillow
  python-decouple==3.8
  ```

---

## ⚙️ Installation & Local Setup

1️⃣ **Clone the repository**
```bash
git clone https://github.com/MatheusBarbosaSE/remove-bg-api.git
cd remove-bg-api
```

2️⃣ **Create and activate a virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3️⃣ **Install dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4️⃣ **Run migrations**
```bash
python manage.py migrate
```

5️⃣ **Run the server**
```bash
python manage.py runserver
```

Your API will be available at:
```
http://127.0.0.1:8000/
```

---

## 🧪 How to Test the API

### 1. Postman (Manual Test)
- Method: **POST**
- URL:
  ```
  http://127.0.0.1:8000/remove-background/
  ```
- Body → **form-data** → Key: `image` (Type: File)

---

### 2. cURL (Terminal Test)

**Windows (PowerShell using `curl.exe`)**
```powershell
curl.exe -X POST http://127.0.0.1:8000/remove-background/ -F "image=@my_image.jpg" -o result.png
```

**Linux/Mac or Git Bash**
```bash
curl -X POST http://127.0.0.1:8000/remove-background/ -F "image=@my_image.jpg" --output result.png
```

- Sends the file and saves the processed PNG as `result.png`
- Open the file to verify the background removal

---

## 3. Automated Tests

You can also validate the API using the automated test suite.  
These tests check different scenarios such as successful background removal, missing or invalid files, wrong HTTP methods, internal errors, and file size limits.

Run all tests with:
```bash
python manage.py test remover.tests.test_api -v 2
```
---

## 📂 Project Structure
```
remove-bg-api/
│
├─ config/              # Django project (settings, urls, wsgi)
├─ remover/             # Main app with views, API endpoints, and tests
├─ manage.py
├─ requirements.txt
├─ .gitignore
├─ LICENSE
└─ README.md
```

---

## 🧠 Key Source Code

### 📥 Serializer (`remover/serializers.py`)
This serializer validates the uploaded image from the request. It ensures that a valid image file is received before processing.
```python
from rest_framework import serializers

class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
```

---

### 🔧 View (`remover/views.py`)
This view receives an image via POST, processes it with rembg, and returns a transparent PNG. It handles image validation, background removal, and error handling.
```python
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
            image_file = serializer.validated_data['image']
            try:
                input_image = Image.open(image_file)
                image_format = input_image.format if input_image.format else 'PNG'
                image_bytes = io.BytesIO()
                input_image.save(image_bytes, format=image_format)
                image_bytes = image_bytes.getvalue()
                output_bytes = remove(image_bytes)
                return HttpResponse(output_bytes, content_type='image/png')
            except UnidentifiedImageError:
                return Response({"error": "The uploaded file is not a valid image."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": "Failed to process image.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

---

### 🔗 URL Routing (`remover/urls.py`)
This defines the route for the API endpoint: `/remove-background/`, handled by the `RemoveBackgroundView`.
```python
from django.urls import path
from .views import RemoveBackgroundView

urlpatterns = [
    path('remove-background/', RemoveBackgroundView.as_view(), name='remove-background'),
]
```

---

### 🔗 Project URLs (`config/urls.py`)
This maps the API routes to the base path `/api/`, and includes Django’s default admin route.
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('remover.urls')),
]
```

---

### ⚙️ Settings (excerpt from `settings.py`)
Key settings for Django to enable REST framework, CORS, and the custom app. This setup is required for the API to run locally and handle cross-origin requests.
```python
INSTALLED_APPS = [
    ...
    'remover',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}
```

---

## ⚡ Notes
- This API is optimized for **local testing and learning**.
- For production deployment, you must configure:
  - `.env` for `SECRET_KEY` and `DEBUG`
  - Whitenoise or cloud storage for static files
  - Set proper `ALLOWED_HOSTS` for your domain or hosting provider