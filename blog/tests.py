from django.test import TestCase
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import BlogPost, Comment

User = get_user_model()


class BlogCommentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123!',
            first_name='Test',
            last_name='User'
        )
        self.post = BlogPost.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            status='published'
        )

    def test_blog_comment_create_get_object_or_404_exists(self):
        from django.shortcuts import get_object_or_404 as g404
        obj = g404(BlogPost, id=self.post.id)
        self.assertEqual(obj.title, 'Test Post')

    def test_blog_comment_create_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/blogs/{self.post.id}/comments/create/',
            {'content': 'Great post!'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_blog_comment_create_unauthenticated(self):
        response = self.client.post(
            f'/api/blogs/{self.post.id}/comments/create/',
            {'content': 'Great post!'}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_blog_list_returns_valid_json(self):
        response = self.client.get('/api/blogs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title', str(response.data))

    def test_comment_list_with_invalid_blog_id(self):
        response = self.client.get('/api/blogs/9999/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
