import os
import uuid
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def upload_temp_image(request):
    if "image" not in request.FILES:
        return JsonResponse({"error": "No image provided"}, status=400)

    image = request.FILES["image"]
    ext = os.path.splitext(image.name)[1] or ".png"
    filename = f"temp_{uuid.uuid4().hex}{ext}"
    date_path = datetime.now().strftime("%Y/%m/%d")
    relative_dir = os.path.join("temp", date_path)
    absolute_dir = os.path.join(settings.MEDIA_ROOT, relative_dir)
    os.makedirs(absolute_dir, exist_ok=True)

    filepath = os.path.join(absolute_dir, filename)
    with open(filepath, "wb") as f:
        for chunk in image.chunks():
            f.write(chunk)

    url = f"{settings.MEDIA_URL}{relative_dir}/{filename}"
    return JsonResponse({"url": url})
