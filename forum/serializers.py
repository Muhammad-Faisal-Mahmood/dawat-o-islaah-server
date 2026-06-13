from rest_framework import serializers
from .models import Question, Answer

class AnswerSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ("id", "content", "author_name", "votes")

    def get_author_name(self, obj):
        if obj.author:
            # Return full name if available, otherwise email
            full_name = f"{obj.author.first_name} {obj.author.last_name}".strip()
            return full_name if full_name else obj.author.email
        return "Anonymous"

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ("id", "title", "content", "topic", "author_name", "votes", "answers")

    def get_author_name(self, obj):
        if obj.author:
            full_name = f"{obj.author.first_name} {obj.author.last_name}".strip()
            return full_name if full_name else obj.author.email
        return "Anonymous"