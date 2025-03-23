# Generated by Django 5.1.7 on 2025-03-23 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('author', models.CharField(blank=True, max_length=100, null=True, verbose_name='author')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('pdf_file', models.FileField(upload_to='books/pdfs/', verbose_name='PDF file')),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='books/covers/', verbose_name='cover image')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='uploaded at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('is_public', models.BooleanField(default=True, verbose_name='is public')),
            ],
            options={
                'verbose_name': 'book',
                'verbose_name_plural': 'books',
                'ordering': ('-uploaded_at',),
            },
        ),
    ]
