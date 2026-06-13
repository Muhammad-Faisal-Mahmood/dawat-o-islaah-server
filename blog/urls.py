# blog/urls.py
from django.urls import path
from .views import BlogPostListAPIView, CommentListAPIView, CommentCreateAPIView, CommentDetailAPIView

# blog/urls.py
urlpatterns = [
    # This will now be: http://127.0.0.1:8000/api/blogs/
    path('', BlogPostListAPIView.as_view(), name='blog-list-api'), 
    
    # This will now be: http://127.0.0.1:8000/api/blogs/5/comments/
    path('<int:blog_id>/comments/', CommentListAPIView.as_view(), name='comment-list'),
    
    # This will now be: http://127.0.0.1:8000/api/blogs/5/comments/create/
    path('<int:blog_id>/comments/create/', CommentCreateAPIView.as_view(), name='comment-create'),
    
    # This will now be: http://127.0.0.1:8000/api/blogs/comments/2/
    path('comments/<int:pk>/', CommentDetailAPIView.as_view(), name='comment-detail'),
]