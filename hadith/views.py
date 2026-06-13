# hadith/views.py
# FULL UPDATED FILE (copy-paste)

from .models import Hadith, Book, Chapter, Baab
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator


def chapters_for_book(request):
    book_id = request.GET.get("book_id")
    if not book_id:
        return JsonResponse([], safe=False)
    chapters = Chapter.objects.filter(book_id=book_id).order_by("chapter_number")
    data = [{"id": c.id, "text": str(c)} for c in chapters]
    return JsonResponse(data, safe=False)


def get_chapters_by_book(request):
    book_id = request.GET.get("book_id")
    if not book_id:
        return JsonResponse([], safe=False)

    try:
        chapters = (
            Hadith.objects.filter(book_id=book_id)
            .exclude(chapter_english__isnull=True)
            .exclude(chapter_english="")
            .order_by("chapter_number")
            .values_list("chapter_english", flat=True)
            .distinct()
        )
        return JsonResponse(list(chapters), safe=False)
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=400)


URDU_TRANSLATION_MAP = {
    "sunan-abu-dawood": "سنن ابو داؤد",
    "abu-dawood": "سنن ابو داؤد",
    "sahih-bukhari": "صحیح بخاری",
    "sahih-muslim": "صحیح مسلم",
    "al-tirmidhi": "جامع ترمذی",
    "tirmidhi": "جامع ترمذی",
    "sunan-nasai": "سنن نسائی",
    "sunan-ibn-e-majah": "سنن ابن ماجہ",
    "ibn-e-majah": "سنن ابن ماجہ",
    "mishkat-al-masabih": "مشکاۃ المصابیح",
    "mishkat": "مشکاۃ المصابیح",
}

DB_BOOK_NAME_MAP = {
    "abu-dawood": "Sunan Abu Dawood",
    "sunan-abu-dawood": "Sunan Abu Dawood",
    "tirmidhi": "Al Tirmidhi",
    "al-tirmidhi": "Al Tirmidhi",
    "mishkat": "Mishkat Al Masabih",
}


def _resolve_book(book_slug):
    if not book_slug:
        return None

    slug = book_slug.lower().strip()

    book = Book.objects.filter(name__iexact=slug).first()
    if book:
        return book

    db_name = DB_BOOK_NAME_MAP.get(slug)
    if db_name:
        book = Book.objects.filter(name__iexact=db_name).first()
        if book:
            return book

    title_name = slug.replace("-", " ").title()
    book = Book.objects.filter(name__iexact=title_name).first()
    if book:
        return book

    contains_name = slug.replace("-", " ")
    book = Book.objects.filter(name__icontains=contains_name).first()
    if book:
        return book

    return None


@api_view(["GET"])
def get_books(request):
    WRITER_DATA = {
        "sahih-bukhari": {"writer": "Imam Bukhari", "death": "256 AH"},
        "sahih-muslim": {"writer": "Imam Muslim", "death": "261 AH"},
        "al-tirmidhi": {"writer": "Imam Tirmidhi", "death": "279 AH"},
        "sunan-abu-dawood": {"writer": "Imam Abu Dawood", "death": "275 AH"},
        "sunan-ibn-e-majah": {"writer": "Imam Ibn Majah", "death": "273 AH"},
        "ibn-e-majah": {"writer": "Imam Ibn Majah", "death": "273 AH"},
        "sunan-nasai": {"writer": "Imam Nasai", "death": "303 AH"},
        "mishkat": {"writer": "Al-Baghawi", "death": "516 AH"},
    }

    books = Book.objects.all().order_by("order")
    data = []

    for b in books:
        slug = b.name.lower().replace(" ", "-")
        info = WRITER_DATA.get(slug, {"writer": "Unknown", "death": "Unknown"})

        chapters_count = (
            b.hadiths.values("chapter_number")
            .distinct()
            .count()
        )

        data.append({
            "name": b.name,
            "slug": slug,
            "hadiths_count": b.hadiths.count(),
            "chapters_count": chapters_count,
            "writerName": info["writer"],
            "writerDeath": info["death"],
        })

    return Response({"status": 200, "books": data})


# ==========================================================
# CHAPTERS API
# FIXED:
# 1. chapter 0 now appears
# 2. global numbering supported
# ==========================================================
@api_view(["GET"])
def get_had_chapters(request):
    book_slug = request.GET.get("book")
    book_obj = _resolve_book(book_slug)

    if not book_obj:
        return Response({"status": 404, "error": "Book not found"}, status=404)

    hadiths = (
        Hadith.objects.filter(book=book_obj)
        .order_by("chapter_number", "hadith_number")
    )

    seen = set()
    chapters = []

    for h in hadiths:
        if h.chapter_number not in seen:
            seen.add(h.chapter_number)

            has_real_urdu = any(ord(c) > 127 for c in (h.chapter_urdu or ""))

            chapters.append({
                "id": h.chapter_number,
                "bookSlug": book_slug,
                "chapterNumber": h.chapter_number,
                "chapterEnglish": h.chapter_english,
                "chapterArabic": h.chapter_arabic or "",
                "chapterUrdu": h.chapter_urdu if has_real_urdu else None,
            })

    return Response({"status": 200, "chapters": chapters})


# ==========================================================
# HADITH API
# FIXED:
# GLOBAL NUMBERING
# ==========================================================
@api_view(["GET"])
def get_hadith(request):
    book_slug = request.GET.get("book")
    chapter_no = request.GET.get("chapter")
    page = request.GET.get("page", 1)

    book_obj = _resolve_book(book_slug)

    if not book_obj:
        return Response({"status": 404, "error": "Book not found"}, status=404)

    # Fetch all baabs for this book to match by number range
    book_baabs = list(Baab.objects.filter(book=book_obj).order_by("start_hadith_number"))

    def find_baab(hadith_number):
        for baab in book_baabs:
            if baab.start_hadith_number <= hadith_number <= baab.end_hadith_number:
                return baab
        return None

    queryset = (
        Hadith.objects.filter(book=book_obj)
        .select_related("book")
        .order_by("hadith_number")   # GLOBAL ORDER
    )

    if chapter_no is not None and str(chapter_no).isdigit():
        queryset = queryset.filter(chapter_number=int(chapter_no))

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(page)

    hadith_data = []

    for h in page_obj:
        baab = h.baab if h.baab_id else find_baab(h.hadith_number)

        hadith_data.append({
            # GLOBAL NUMBERING
            "hadithNumber": h.hadith_number,

            "hadithArabic": h.arabic_text,
            "hadithEnglish": h.english_text,
            "hadithUrdu": h.urdu_text,
            "reference": h.reference,
            "status": h.status,
            "detailedExplanation": h.detailed_explanation,

            "bookSlug": book_slug,
            "bookNameEnglish": h.book.name,
            "bookNameUrdu": URDU_TRANSLATION_MAP.get(book_slug, h.book.name),

            "baab": {
                "nameUrdu": baab.baab_name_urdu if baab else None,
                "nameEnglish": baab.baab_name_english if baab else None,
            } if baab else None,

            "chapter": {
                "chapterNumber": h.chapter_number,
                "chapterEnglish": h.chapter_english,
                "chapterArabic": h.chapter_arabic,
                "chapterUrdu": h.chapter_urdu or h.chapter_english,
            },
        })

    return Response({
        "status": 200,
        "hadiths": {
            "data": hadith_data,
            "last_page": paginator.num_pages,
        },
    })


@api_view(["GET"])
def fetch_hadith_from_api(request):
    book_slug = request.GET.get("book")

    if not book_slug:
        return Response({"error": "Required"}, status=400)

    normalized_name = DB_BOOK_NAME_MAP.get(
        book_slug,
        book_slug.replace("-", " ").title()
    )

    Book.objects.get_or_create(name=normalized_name)

    return Response({"message": "Running in background"})
