import os, threading
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'cover_thumbnail',
        'title', 'author', 'total_pages',
        'processing_status_display',
        'read_count_display', 'download_count_display',
        'uploaded_at', 'is_public'
    )
    list_display_links = ('cover_thumbnail', 'title')
    list_filter = ('is_public', 'is_split', 'processing_status', 'uploaded_at')
    search_fields = ('title', 'author', 'description')
    date_hierarchy = 'uploaded_at'
    ordering = ('-uploaded_at',)
    readonly_fields = ('read_count', 'download_count', 'total_pages', 'is_split',
                        'processing_status', 'cover_preview', 'pdf_preview')

    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'description')
        }),
        ('Files', {
            'fields': ('pdf_file', 'cover_image', 'cover_preview')
        }),
        ('Processing', {
            'fields': ('processing_status', 'is_split', 'total_pages'),
        }),
        ('Statistics', {
            'fields': ('read_count', 'download_count'),
        }),
        ('Visibility', {
            'fields': ('is_public',),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_public', 'make_private', 'reset_counters', 'reprocess_books']

    @admin.display(description='Cover')
    def cover_thumbnail(self, obj):
        if obj.cover_image and hasattr(obj.cover_image, 'url'):
            url = obj.cover_image.url
            return format_html(
                '<img src="{}" style="width:50px;height:70px;object-fit:cover;border-radius:4px" />',
                url
            )
        return format_html('<span style="color:#999">No cover</span>')

    @admin.display(description='Cover Preview')
    def cover_preview(self, obj):
        if obj.cover_image and hasattr(obj.cover_image, 'url'):
            url = obj.cover_image.url
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:400px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.15)" />',
                url
            )
        return format_html('<span style="color:#999;font-style:italic">No cover image uploaded</span>')

    @admin.display(description='PDF Preview')
    def pdf_preview(self, obj):
        if obj.pdf_file and hasattr(obj.pdf_file, 'url'):
            return format_html(
                '<a href="{}" target="_blank" style="display:inline-block;padding:8px 16px;'
                'background:#1E3A5F;color:white;border-radius:6px;text-decoration:none">'
                'View PDF &#8599;</a>',
                obj.pdf_file.url
            )
        return format_html('<span style="color:#999;font-style:italic">No PDF file</span>')

    @admin.display(description='Status', ordering='processing_status')
    def processing_status_display(self, obj):
        colors = {
            'pending': '#f59e0b',
            'processing': '#3b82f6',
            'completed': '#10b981',
            'failed': '#ef4444',
        }
        labels = {
            'pending': 'Pending',
            'processing': 'Processing',
            'completed': 'Completed',
            'failed': 'Failed',
        }
        color = colors.get(obj.processing_status, '#6b7280')
        label = labels.get(obj.processing_status, obj.processing_status)
        return format_html(
            '<span style="display:inline-block;padding:3px 10px;border-radius:12px;'
            'color:white;font-weight:600;font-size:11px;background:{}">{}</span>',
            color, label
        )

    @admin.display(description='Reads', ordering='read_count')
    def read_count_display(self, obj):
        return format_html(
            '<span style="color:#10b981;font-weight:bold">{}</span>',
            obj.read_count
        )

    @admin.display(description='Downloads', ordering='download_count')
    def download_count_display(self, obj):
        return format_html(
            '<span style="color:#3b82f6;font-weight:bold">{}</span>',
            obj.download_count
        )

    @admin.action(description='Mark selected as public')
    def make_public(self, request, queryset):
        queryset.update(is_public=True)

    @admin.action(description='Mark selected as private')
    def make_private(self, request, queryset):
        queryset.update(is_public=False)

    @admin.action(description='Reset read & download counters')
    def reset_counters(self, request, queryset):
        queryset.update(read_count=0, download_count=0)

    @admin.action(description='Reprocess selected books (split + OCR)')
    def reprocess_books(self, request, queryset):
        for obj in queryset:
            Book.objects.filter(pk=obj.pk).update(processing_status='pending')
            from .tasks import _process_book_pdf_sync
            t = threading.Thread(target=_process_book_pdf_sync, args=[obj.pk])
            t.start()
        self.message_user(request, f'Reprocessing started for {queryset.count()} book(s).')

    def save_model(self, request, obj, form, change):
        is_new = not change or obj.pk is None
        pdf_changed = form.changed_data and 'pdf_file' in form.changed_data

        if is_new:
            obj.processing_status = 'pending'

        super().save_model(request, obj, form, change)

        if is_new or pdf_changed:
            total = obj.render_first_page()
            # Store total_pages immediately so admin shows correct count
            if total > 0:
                Book.objects.filter(pk=obj.pk).update(total_pages=total)
                obj.total_pages = total
            # Full processing in background
            from .tasks import _process_book_pdf_sync
            Book.objects.filter(pk=obj.pk).update(processing_status='processing')
            t = threading.Thread(target=_process_book_pdf_sync, args=[obj.pk])
            t.start()

    class Media:
        css = {
            'all': ('admin/css/books.css',)
        }
