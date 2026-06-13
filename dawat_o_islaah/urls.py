from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt # Add this import at the top
from ckeditor_uploader import views as ck_views
from .upload_views import upload_temp_image

urlpatterns = [

    # =============================
    # Admin
    # =============================
    path('admin/', admin.site.urls),

    # =============================
    # Authentication
    # =============================
    path('api/auth/', include('user_management.urls')),

    # =============================
    # Core APIs
    # =============================
    path('api/blogs/', include('blog.urls')),
    path('api/books/', include('books.urls')),
    path('api/masails/', include('masails.urls')),
    path('api/questions/', include('qna.urls')),
    path('api/forum/', include('forum.urls')),

    # =============================
    # Hadith APIs
    # =============================
    path('api/hadith/', include('hadith.urls')),

    # =============================
    # Quran APIs
    # =============================
    path('quran/', include('quran.urls')),

    # =============================
    # CKEditor
    # =============================
    path('ckeditor/upload/', csrf_exempt(ck_views.upload), name='ckeditor_upload'),
    path('ckeditor/browse/', ck_views.browse, name='ckeditor_browse'),

    # =============================
    # Temp Image Upload (WhatsApp share)
    # =============================
    path('api/upload-temp-image/', upload_temp_image, name='upload_temp_image'),
]


# =============================
# Serve Media Files (Dev Only)
# =============================
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# =============================
# Admin Branding
# =============================
admin.site.site_header = "Dawat O Islaah Admin"
admin.site.site_title = "Dawat O Islaah Admin Portal"
admin.site.index_title = "Welcome to Dawat O Islaah Portal"
