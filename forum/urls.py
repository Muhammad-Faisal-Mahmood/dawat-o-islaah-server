from django.urls import path
from . import views

urlpatterns = [
    path("topics/", views.topics_list), # <--- ADD THIS
    path("questions/", views.questions_list),
    path("questions/<int:question_id>/answers/", views.add_answer),
    path("vote/", views.vote),
]
