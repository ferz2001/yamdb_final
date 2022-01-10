from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategorieViewSet, CommentViewSet, GenreViewSet,
                    RegisterView, ReviewViewSet, TitleViewSet, TokenView,
                    UserViewSet)

app_name = 'api'

api_router = DefaultRouter()
api_router.register('users', UserViewSet, basename='users')
api_router.register('categories', CategorieViewSet, basename='categories')
api_router.register('genres', GenreViewSet, basename='genres')
api_router.register('titles', TitleViewSet, basename='titles')
api_router.register(r'^titles/(?P<title_id>\d+)/reviews',
                    ReviewViewSet,
                    basename='reviews')
api_router.register(
    r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
urlpatterns = [
    path('v1/auth/signup/', RegisterView.as_view(), name='register'),
    path('v1/auth/token/', TokenView.as_view(), name='get_token'),
    path('v1/', include(api_router.urls)),
]
