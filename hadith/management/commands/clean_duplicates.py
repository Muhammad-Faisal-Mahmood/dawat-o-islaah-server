from django.core.management.base import BaseCommand
from django.db.models import Count
from hadith.models import Hadith


class Command(BaseCommand):
    help = "Remove duplicate hadith records safely"

    def handle(self, *args, **kwargs):

        duplicates = (
            Hadith.objects
            .values("book", "hadith_number")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
        )

        self.stdout.write(f"Duplicate groups found: {duplicates.count()}")

        deleted_count = 0

        for item in duplicates:

            # Get all IDs for this duplicate group
            ids = list(
                Hadith.objects
                .filter(
                    book=item["book"],
                    hadith_number=item["hadith_number"]
                )
                .order_by("id")
                .values_list("id", flat=True)
            )

            # Keep first ID, delete the rest
            ids_to_delete = ids[1:]

            if ids_to_delete:
                deleted_count += len(ids_to_delete)
                Hadith.objects.filter(id__in=ids_to_delete).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Total duplicate records deleted: {deleted_count}"
            )
        )