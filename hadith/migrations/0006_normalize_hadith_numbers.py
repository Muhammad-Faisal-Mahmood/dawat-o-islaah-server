from django.db import migrations


def normalize_numbers(apps, schema_editor):
    Hadith = apps.get_model("hadith", "Hadith")
    Book = apps.get_model("hadith", "Book")

    OFFSET = 1000000

    for book in Book.objects.all():
        qs = Hadith.objects.filter(book=book)

        if not qs.exists():
            continue

        # STEP 1: move all far away
        for h in qs.order_by("-hadith_number"):
            h.hadith_number = h.hadith_number + OFFSET
            h.save(update_fields=["hadith_number"])

        # refresh queryset
        qs = Hadith.objects.filter(book=book)

        min_num = qs.order_by("hadith_number").first().hadith_number
        original_min = min_num - OFFSET

        shift = original_min - 1

        # STEP 2: normalize back
        for h in qs.order_by("hadith_number"):
            h.hadith_number = h.hadith_number - OFFSET - shift
            h.save(update_fields=["hadith_number"])


class Migration(migrations.Migration):

    dependencies = [
        ("hadith", "0005_shift_hadith_numbers"),
    ]

    operations = [
        migrations.RunPython(normalize_numbers),
    ]
