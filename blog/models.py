from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from PIL import Image
from ckeditor_uploader.fields import RichTextUploadingField

BLOG_COVER_WIDTH = 1200
BLOG_COVER_HEIGHT = 630

def validate_blog_cover_image(image):
    img = Image.open(image)
    width, height = img.size
    if width != BLOG_COVER_WIDTH or height != BLOG_COVER_HEIGHT:
        raise ValidationError(
            f'Image must be exactly {BLOG_COVER_WIDTH}×{BLOG_COVER_HEIGHT} pixels. '
            f'Uploaded image is {width}×{height} pixels.'
        )

class BlogPost(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique_for_date='created_at')
    content = RichTextUploadingField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    featured_image = models.ImageField(
        upload_to='blog_images/',
        blank=True,
        null=True,
        validators=[validate_blog_cover_image]
    )

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog_detail', args=[self.slug])


class Comment(models.Model):
    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.blog_post.title}"
