from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_booksessiondownload_booksessionread'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='processing_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('processing', 'Processing'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
