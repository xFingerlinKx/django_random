import pytz
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import parsers, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from test_api.models import Token
from .serializers import UserSerializer


class CreateUserAPIView(CreateAPIView):
    """ Create a new user - possible without token. """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer


class CustomAuthToken(ObtainAuthToken):
    """
    Get new User token with username and password.

    Example:
            Request data:
            {
                "username": "xFingerlinKx",
                "password": "admin"
            }
            Response data:
            {
                "token": "575171911ab239751d887dc4ff097121f4083122"
            }
    """
    parser_classes = (parsers.JSONParser,)
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            utc_now = timezone.now()
            utc_now = utc_now.replace(tzinfo=pytz.utc)

            token, created = Token.objects.get_or_create(
                user=user,
                created__gt=utc_now - settings.TOKEN_TTL
            )

            return Response({
                'token': token.key,
                'user_id': user.pk,
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomAuthLogOut(APIView):
    """ Logout user - deactivate user token """
    parser_classes = (parsers.JSONParser,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def post(self, request):
        return self.logout(request)

    # noinspection PyMethodMayBeStatic
    def logout(self, request):
        token = getattr(request, 'auth', None)

        if token and token.is_active:
            token.is_active = False
            token.save()
            return Response({
                'detail': f'Successfully logged out.\n Token {token.key} was deactivated.'
            }, status=status.HTTP_200_OK,)

        logout(request)
        return Response({
            'detail': 'Bad request. Wrong credentials.'
        }, status=status.HTTP_401_UNAUTHORIZED)


class GetUserDataApiView(APIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    # noinspection PyMethodMayBeStatic
    def get(self, request):
        content = {
            'user': str(request.user),
            'auth': str(request.auth),
        }
        return Response(content)


# curl -X  GET -H 'Authorization: Token 02a6fe8d7d82fc83f5d4e51e362c6044335b7ed0' http://127.0.0.1:8000/api/users/8/
# todo: можно реализовать через viewsets ModelViewSet
class UserList(ListAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = User.objects.all()
    serializer_class = UserSerializer
