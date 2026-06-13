# qna/urls.py
from django.urls import path
from .views import (
    PublicQuestionListAPI,
    UserQuestionCreateAPI,
    UserQuestionListAPI,
    UserQuestionDetailAPI,
    CategoryListAPI,
    ToggleBookmarkAPI,
    IncrementViewAPI,
    IncrementDownloadAPI,
    CreateAnswerAPI,
)

urlpatterns = [
    path('', PublicQuestionListAPI.as_view(), name='public-questions'),
    path('categories/', CategoryListAPI.as_view(), name='categories'),
    path('<int:pk>/toggle-save/', ToggleBookmarkAPI.as_view(), name='toggle-save'),
    path('create/', UserQuestionCreateAPI.as_view(), name='create-question'),
    path('my/', UserQuestionListAPI.as_view(), name='my-questions'),
    path('<int:pk>/', UserQuestionDetailAPI.as_view(), name='user-question-detail'),
    path('<int:pk>/view/', IncrementViewAPI.as_view(), name='increment-view'),
    path('<int:pk>/download/', IncrementDownloadAPI.as_view(), name='increment-download'),
    path('<int:pk>/answer/', CreateAnswerAPI.as_view(), name='create-answer'),
]
