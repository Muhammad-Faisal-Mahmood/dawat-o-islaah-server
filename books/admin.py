import threading
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'total_pages',
        'read_count_display', 'download_count_display',
        'uploaded_at', 'is_public'
    )
    list_filter = ('is_public', 'is_split', 'uploaded_at')
    search_fields = ('title', 'author', 'description')
    date_hierarchy = 'uploaded_at'
    ordering = ('-uploaded_at',)
    readonly_fields = ('read_count', 'download_count', 'total_pages', 'is_split')

    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'description')
        }),
        ('Files', {
            'fields': ('pdf_file', 'cover_image')
        }),
        ('Statistics', {
            'fields': ('total_pages', 'is_split', 'read_count', 'download_count'),
        }),
        ('Visibility', {
            'fields': ('is_public',),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_public', 'make_private', 'reset_counters']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change or (form.changed_data and 'pdf_file' in form.changed_data):
            self._set_page_count_sync(obj)
            from .tasks import _process_book_pdf_sync
            t = threading.Thread(target=_process_book_pdf_sync, args=[obj.pk])
            t.start()

    def _set_page_count_sync(self, obj):
        try:
            pdf_path = obj.pdf_file.path
            if pdf_path.lower().endswith('.pdf'):
                import fitz
                doc = fitz.open(pdf_path)
                total = doc.page_count
                doc.close()
                if total:
                    Book.objects.filter(pk=obj.pk).update(total_pages=total)
                    obj.total_pages = total
        except Exception:
            pass

    @admin.display(description='📖 Reads', ordering='read_count')
    def read_count_display(self, obj):
        return format_html(
            '<span style="color: green; font-weight: bold;">{}</span>',
            obj.read_count
        )

    @admin.display(description='⬇️ Downloads', ordering='download_count')
    def download_count_display(self, obj):
        return format_html(
            '<span style="color: blue; font-weight: bold;">{}</span>',
            obj.download_count
        )

    @admin.action(description='Mark selected books as public')
    def make_public(self, request, queryset):
        queryset.update(is_public=True)

    @admin.action(description='Mark selected books as private')
    def make_private(self, request, queryset):
        queryset.update(is_public=False)

    @admin.action(description='Reset read & download counters to 0')
    def reset_counters(self, request, queryset):
        queryset.update(read_count=0, download_count=0)
