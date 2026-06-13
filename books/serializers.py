from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    pages_url_prefix = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description',
            'pdf_file', 'cover_image',
            'total_pages', 'is_split', 'pages_url_prefix',
            'read_count', 'download_count',
            'uploaded_at', 'updated_at', 'is_public',
            'content_type',
            'extracted_text',
        ]

    def get_pages_url_prefix(self, obj):
        if obj.is_split:
            request = self.context.get('request')
            prefix = f'/media/books/pages/{obj.pk}/'
            if request:
                return request.build_absolute_uri(prefix)
            return prefix
        return None
