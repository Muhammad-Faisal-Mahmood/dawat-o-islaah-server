from django.db import migrations


def shift_numbers(apps, schema_editor):
    Hadith = apps.get_model("hadith", "Hadith")

    for h in Hadith.objects.all().order_by("-hadith_number"):
        h.hadith_number += 1
        h.save(update_fields=["hadith_number"])


class Migration(migrations.Migration):

    dependencies = [
        ("hadith", "0004_hadith_chapter_hadith_id"),
    ]

    operations = [
        migrations.RunPython(shift_numbers),
    ]
