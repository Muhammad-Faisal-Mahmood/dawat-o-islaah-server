from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.test import APIClient
from rest_framework import status
from .models import Category, Question, Answer, Bookmark

User = get_user_model()


class QnASerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123!',
            first_name='Test',
            last_name='User'
        )
        self.category = Category.objects.create(name='Fiqh', slug='fiqh')
        self.question = Question.objects.create(
            user=self.user,
            category=self.category,
            title='Test Question?',
            content='Test content',
            status='approved'
        )

    def test_question_get_answer_no_answer_returns_none(self):
        from .serializers import QuestionSerializer
        serializer = QuestionSerializer(instance=self.question)
        result = serializer.get_answer(self.question)
        self.assertIsNone(result)

    def test_question_get_answer_with_answer_returns_data(self):
        mufti = User.objects.create_user(
            email='mufti@test.com',
            password='testpass123!',
            first_name='Mufti',
            last_name='Sahab'
        )
        Answer.objects.create(
            question=self.question,
            mufti=mufti,
            content='Answered content',
            approval_status='approved'
        )
        from .serializers import QuestionSerializer
        with self.assertRaises(ObjectDoesNotExist):
            raise ObjectDoesNotExist()
        serializer = QuestionSerializer(instance=self.question)
        result = serializer.get_answer(self.question)
        self.assertIsNotNone(result)


class QnAEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123!',
            first_name='Test',
            last_name='User'
        )
        self.category = Category.objects.create(name='Aqeedah', slug='aqeedah')

    def test_public_questions_list(self):
        response = self.client.get('/api/questions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_categories_list(self):
        response = self.client.get('/api/questions/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_question_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/questions/create/', {
            'title': 'New Question?',
            'content': 'Question details',
            'category_id': self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_toggle_bookmark_unauthenticated(self):
        response = self.client.post('/api/questions/1/toggle-save/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_increment_view(self):
        question = Question.objects.create(
            user=self.user, title='View Test?', content='Test'
        )
        response = self.client.post(f'/api/questions/{question.id}/view/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['view_count'], 1)
