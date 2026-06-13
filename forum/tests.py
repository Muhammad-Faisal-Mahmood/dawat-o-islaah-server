from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Question, Answer

User = get_user_model()


class ForumModelTests(TestCase):
    def test_answer_str_with_null_question(self):
        user = User.objects.create_user(
            email='author@test.com',
            password='testpass123!',
            first_name='Author'
        )
        answer = Answer.objects.create(
            question=None,
            content='Test answer',
            author=user
        )
        result = str(answer)
        self.assertIn('Deleted Question', result)
        self.assertIn('author@test.com', result)

    def test_answer_str_with_valid_question(self):
        user = User.objects.create_user(
            email='author@test.com',
            password='testpass123!'
        )
        question = Question.objects.create(
            title='Test Question?',
            content='Details',
            author=user
        )
        answer = Answer.objects.create(
            question=question,
            content='Test answer',
            author=user
        )
        result = str(answer)
        self.assertIn('Test Question?', result)


class ForumEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123!',
            first_name='Test',
            last_name='User'
        )

    def test_topics_list(self):
        response = self.client.get('/api/forum/topics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_questions_list(self):
        response = self.client.get('/api/forum/questions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_question_unauthenticated(self):
        response = self.client.post('/api/forum/questions/', {
            'title': 'Test?',
            'content': 'Details',
            'topic': 'Quran'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_answer(self):
        question = Question.objects.create(
            title='Test?',
            content='Details',
            author=self.user
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/forum/questions/{question.id}/answers/',
            {'content': 'An answer'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
