from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import F
from .models import Book, BookSessionRead, BookSessionDownload
from .serializers import BookSerializer


class BookListAPIView(generics.ListAPIView):
    queryset = Book.objects.filter(is_public=True).order_by('-uploaded_at')
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author', 'description']


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def track_book_read(request, pk):
    try:
        book = Book.objects.get(pk=pk, is_public=True)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key

    with transaction.atomic():
        read_record, created = BookSessionRead.objects.get_or_create(
            session_key=session_key, book=book
        )
        if created:
            Book.objects.filter(pk=pk).update(read_count=F('read_count') + 1)

        book.refresh_from_db()

    return Response({'read_count': book.read_count}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def track_book_download(request, pk):
    try:
        book = Book.objects.get(pk=pk, is_public=True)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key

    with transaction.atomic():
        download_record, created = BookSessionDownload.objects.get_or_create(
            session_key=session_key, book=book
        )
        if created:
            Book.objects.filter(pk=pk).update(download_count=F('download_count') + 1)

        book.refresh_from_db()

    return Response({'download_count': book.download_count}, status=status.HTTP_200_OK)
