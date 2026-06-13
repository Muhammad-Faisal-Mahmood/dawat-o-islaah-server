from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer
from django.shortcuts import get_object_or_404

# =========================
# Questions
# =========================

@api_view(["GET"])
def topics_list(request):
    # This provides the categories your React app is looking for
    topics = ["Quran", "Hadith", "Fiqh", "General"]
    return Response(topics)

@api_view(["GET", "POST"])
def questions_list(request):
    if request.method == "GET":
        questions = Question.objects.all().order_by("-created_at")
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=401)

        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            # Associate the question with the logged-in user
            serializer.save(author=request.user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# =========================
# Answers
# =========================

@api_view(["POST"])
def add_answer(request, question_id):
    # 1. Check authentication first
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required to answer"}, status=401)

    question = get_object_or_404(Question, id=question_id)
    
    # 2. Don't manually inject IDs into request.data if you can avoid it
    serializer = AnswerSerializer(data=request.data)
    
    if serializer.is_valid():
        # 3. Pass the objects directly during save
        serializer.save(author=request.user, question=question)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# =========================
# Voting
# =========================

@api_view(["POST"])
def vote(request):
    """
    Body: { questionId, answerId (optional), type: 'up'/'down' }
    """
    question_id = request.data.get("questionId")
    answer_id = request.data.get("answerId")
    vote_type = request.data.get("type")

    if not question_id and not answer_id:
        return Response({"error": "questionId or answerId required"}, status=400)

    delta = 1 if vote_type == "up" else -1

    if answer_id:
        try:
            answer = Answer.objects.get(id=answer_id)
            answer.votes += delta
            answer.save()
        except Answer.DoesNotExist:
            return Response({"error": "Answer not found"}, status=404)
    else:
        try:
            question = Question.objects.get(id=question_id)
            question.votes += delta
            question.save()
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

    return Response({"success": True})
