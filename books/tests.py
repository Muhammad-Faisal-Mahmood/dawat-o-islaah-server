from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Book


class BookSerializerTests(TestCase):
    def test_pages_url_prefix_no_request_context(self):
        from .serializers import BookSerializer
        book = Book.objects.create(title='Test Book', pdf_file=None)
        book.is_split = False
        serializer = BookSerializer(instance=book, context={})
        result = serializer.get_pages_url_prefix(book)
        self.assertIsNone(result)


class BookEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            is_public=True,
            read_count=0,
            download_count=0
        )

    def test_book_list(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_track_read(self):
        response = self.client.post(f'/api/books/{self.book.id}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['read_count'], 1)

    def test_track_read_not_found(self):
        response = self.client.post('/api/books/99999/read/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_track_download(self):
        response = self.client.post(f'/api/books/{self.book.id}/download/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['download_count'], 1)
