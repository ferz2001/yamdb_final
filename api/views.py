from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django_filters.rest_framework.filters import CharFilter
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Categorie, Comment, Genre, Review, Title, User

from .permissions import (IsAdmin, IsAdminOrReadOnly, IsAuthor, IsModerator,
                          IsSuperuser)
from .serializers import (CategorieSerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, TitleSerializer,
                          TitleWriteSerializer, UserSerializer)
from .utilities import get_confirmation_code, send_confirmation_code_email


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        confirmation_code = get_confirmation_code()
        data = {
            'email': email,
            'username': username,
            'confirmation_code': confirmation_code
        }
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        try:
            send_confirmation_code_email(email, confirmation_code)
        except Exception:
            print('email не ушел :)')
        data.pop('confirmation_code')
        return Response(data, status=status.HTTP_200_OK)


class TokenView(APIView):
    permission_classes = (AllowAny,)

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def post(self, request):
        username = request.data.get('username')
        if username is None:
            response = {'username': 'Вы забыли указать username'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != request.data.get('confirmation_code'):
            response = {'confirmation_code': 'Invalid confirmation code'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response = {'token': self.get_token(user)}
        return Response(response, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)
    permission_classes = (IsAuthenticated, IsSuperuser | IsAdmin,)

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,),
            methods=['GET', 'PATCH'], url_path='me')
    def get_or_patch_yourself(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            instance=request.user,
            data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly | IsSuperuser,)


class CreateListDestroyMixin(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.DestroyModelMixin,
                             viewsets.GenericViewSet):
    pass


class GenreViewSet(CreateListDestroyMixin):
    queryset = Genre.objects.get_queryset().order_by('id')
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly | IsSuperuser,)


class TitleFilter(FilterSet):
    genre = CharFilter(field_name='genre__slug')
    category = CharFilter(field_name='categorie__slug')
    name = CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'year')


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.get_queryset().order_by('id')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly | IsSuperuser,)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TitleSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.get_queryset().order_by('id')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor | IsModerator
                          | IsAdminOrReadOnly | IsSuperuser]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        return Review.objects.filter(title=title_id).order_by('id')

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, id=title_id)
        if self.request.user.reviews.filter(title=title).exists():
            raise ParseError('Нельзя добавить еще один отзыв :)')
        serializer.save(author=self.request.user,
                        title=title)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.get_queryset().order_by('id')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor | IsModerator
                          | IsAdminOrReadOnly | IsSuperuser]

    def get_queryset(self):
        review_id = self.kwargs['review_id']
        return Comment.objects.filter(review=review_id).order_by('id')

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        title = get_object_or_404(Title, id=title_id)
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user,
                        title=title,
                        review=review)
