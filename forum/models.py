from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField

class Question(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextField()
    topic = models.CharField(max_length=100, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_questions",
	null=True,  # Add this
        blank=True  # Add this
    )
    votes = models.IntegerField(default=0)  # <-- NEW
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
	null=True,  # Add this
        blank=True  # Add this
    )
    content = RichTextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_answers"
    )
    votes = models.IntegerField(default=0)  # <-- NEW
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        question_title = self.question.title if self.question else "Deleted Question"
        return f"Answer by {self.author} for '{question_title}'"
