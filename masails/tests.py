from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Masail, Category


class MasailSerializerTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Cat', slug='test-cat')

    def test_get_image_no_request_context(self):
        from .serializers import MasailSerializer
        masail = Masail.objects.create(
            title='Test',
            slug='test',
            content='Content',
            category=self.category,
            status='published'
        )
        serializer = MasailSerializer(instance=masail, context={})
        result = serializer.get_image(masail)
        self.assertIsNone(result)


class MasailEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Test', slug='test')
        self.masail = Masail.objects.create(
            title='Published Masail',
            slug='published',
            content='Content',
            category=self.category,
            status='published'
        )

    def test_masail_list(self):
        response = self.client.get('/api/masails/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_masail_search(self):
        response = self.client.get('/api/masails/?search=Published')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_masail_list_returns_valid_json(self):
        response = self.client.get('/api/masails/')
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)
