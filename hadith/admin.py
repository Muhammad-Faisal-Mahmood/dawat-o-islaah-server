
# hadith/admin.py
# FULL UPDATED FILE
# Copy paste complete file

import re

from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Hadith, Baab, Book, Chapter




# ======================================================
# FORM
# ======================================================
class HadithAdminForm(forms.ModelForm):
    arabic_text = forms.CharField(widget=CKEditorWidget(), required=False)
    english_text = forms.CharField(widget=CKEditorWidget(), required=False)
    reference = forms.CharField(widget=CKEditorWidget(), required=False)
    urdu_text = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = Hadith
        fields = "__all__"


# ======================================================
# BOOK ADMIN
# ======================================================
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    ordering = ("order",)


# ======================================================
# CHAPTER ADMIN
# ======================================================
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("chapter_number", "chapter_english", "book")
    list_filter = ("book",)
    search_fields = ("chapter_english", "chapter_urdu", "chapter_arabic")
    ordering = ("book", "chapter_number")


# ======================================================
# BAAB ADMIN FORM
# ======================================================
class BaabAdminForm(forms.ModelForm):
    chapter = forms.ModelChoiceField(
        queryset=Chapter.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "chapter-select"})
    )

    class Meta:
        model = Baab
        fields = "__all__"

    class Media:
        js = ("admin/js/baab_admin.js",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        book_id = None
        if self.instance.pk:
            book_id = self.instance.book_id
        elif self.is_bound:
            try:
                book_id = int(self.data.get("book"))
            except (ValueError, TypeError):
                pass

        if book_id:
            self.fields["chapter"].queryset = Chapter.objects.filter(
                book=book_id
            ).order_by("chapter_number")
        else:
            self.fields["chapter"].queryset = Chapter.objects.none()

    URDU_RE = re.compile(
        r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
    )

    def clean_baab_name_urdu(self):
        value = self.cleaned_data.get("baab_name_urdu", "")
        if value and not self.URDU_RE.search(value):
            raise forms.ValidationError(
                "This field appears to be in English/Latin script. "
                "Please enter the baab name in Urdu script."
            )
        return value

    def clean_baab_name_english(self):
        value = self.cleaned_data.get("baab_name_english", "")
        if value and self.URDU_RE.search(value):
            raise forms.ValidationError(
                "This field appears to be in Urdu/Arabic script. "
                "Please enter the baab name in English/Latin script."
            )
        return value


# ======================================================
# BAAB ADMIN
# ======================================================
@admin.register(Baab)
class BaabAdmin(admin.ModelAdmin):
    form = BaabAdminForm

    list_display = (
        "baab_name_urdu",
        "baab_name_english",
        "book",
        "get_chapter_display",
        "start_hadith_number",
        "end_hadith_number",
    )

    list_filter = ("book",)

    fieldsets = (
        ("Book & Chapter", {
            "fields": ("book", "chapter")
        }),
        ("Baab Names", {
            "fields": ("baab_name_urdu", "baab_name_english")
        }),
        ("Hadith Range", {
            "fields": ("start_hadith_number", "end_hadith_number")
        }),
    )

    @admin.display(description="Chapter")
    def get_chapter_display(self, obj):
        if obj.chapter:
            return f"{obj.chapter.chapter_number}. {obj.chapter.chapter_english}"
        return obj.chapter_english or "-"

    def save_model(self, request, obj, form, change):
        from hadith.models import Hadith
        super().save_model(request, obj, form, change)
        updated = Hadith.objects.filter(
            book=obj.book,
            hadith_number__gte=obj.start_hadith_number,
            hadith_number__lte=obj.end_hadith_number
        ).exclude(baab=obj).update(baab=obj)
        if updated:
            self.message_user(request, f"Linked {updated} hadith(s) to this baab.")


# ======================================================
# CHAPTER FILTER
# ======================================================
class ChapterNumberFilter(admin.SimpleListFilter):
    title = "Chapter"
    parameter_name = "chapter_num"

    def lookups(self, request, model_admin):
        qs = Hadith.objects.all()

        book_id = request.GET.get("book__id__exact")
        if book_id:
            qs = qs.filter(book_id=book_id)

        chapters = (
            qs.order_by("chapter_number")
            .values_list("chapter_number", "chapter_english")
            .distinct()
        )

        seen = set()
        results = []

        for num, name in chapters:
            if num not in seen:
                seen.add(num)
                results.append((str(num), f"{num}. {name}"))

        return results

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(chapter_number=int(self.value()))
        return queryset


# ======================================================
# HADITH ADMIN
# ======================================================
@admin.register(Hadith)
class HadithAdmin(admin.ModelAdmin):
    form = HadithAdminForm

    # GLOBAL HADITH NUMBER DISPLAY
    list_display = (
        "chapter_hadith_id",
        "book",
        "chapter_number",
        "chapter_english",
        "chapter_urdu",
        "chapter_arabic",
        "get_baab",
        "get_baab_english",
        "status",
        "detailed_explanation",
    )

    list_display_links = ("chapter_hadith_id",)

    search_fields = (
        "chapter_hadith_id",
        "hadith_number",
        "chapter_english",
        "chapter_urdu",
        "chapter_arabic",
        "reference",
        "status",
        "detailed_explanation",
        "baab__baab_name_urdu",
        "baab__baab_name_english",
        "book__name",
    )

    list_filter = (
        "book",
        ChapterNumberFilter,
    )

    # IMPORTANT FIX
    # use global hadith_number instead of chapter_hadith_id
    ordering = (
        "book__order",
        "chapter_hadith_id",
    )

    list_per_page = 50

    fieldsets = (
        ("Main Info", {
            "fields": (
                "book",
                "chapter_number",
                "chapter_hadith_id",
                "hadith_number",
                "baab",
            )
        }),

        ("Chapter Names", {
            "fields": (
                "chapter_english",
                "chapter_urdu",
                "chapter_arabic",
            )
        }),

        ("Texts", {
            "fields": (
                "arabic_text",
                "urdu_text",
                "english_text",
            )
        }),

        ("Other", {
            "fields": (
                "reference",
                "updated_by",
                "status",
                "detailed_explanation",
            )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "book",
            "baab"
        )

    @admin.display(description="Baab Urdu")
    def get_baab(self, obj):
        return obj.baab.baab_name_urdu if obj.baab else "-"

    @admin.display(description="Baab English")
    def get_baab_english(self, obj):
        return obj.baab.baab_name_english if obj.baab and obj.baab.baab_name_english else "-"
