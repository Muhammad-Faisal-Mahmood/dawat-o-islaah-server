from django.urls import path
from .views import BookListAPIView, track_book_read, track_book_download

urlpatterns = [
    path('', BookListAPIView.as_view(), name='book-list-api'),
    path('<int:pk>/read/', track_book_read, name='book-track-read'),
    path('<int:pk>/download/', track_book_download, name='book-track-download'),
]
