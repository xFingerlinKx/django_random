import datetime

from django.contrib.auth.models import User
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
    # todo: уточнить по поводу необходимости токена???
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get(self, request):
        return Response(request.data)


class CustomAuthToken(ObtainAuthToken):
    """
    Get User token with username and password.

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

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print('serializer ====', serializer)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            if not created:
                token.created = datetime.datetime.utcnow()
                token.save()

            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserDataApiView(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {
            'user': str(request.user),
            'auth': str(request.auth),
        }
        return Response(content)


# curl -X  GET -H 'Authorization: Token 02a6fe8d7d82fc83f5d4e51e362c6044335b7ed0' http://127.0.0.1:8000/api/users/8/
# admin token 1fcd9f7729badc0c6ed0ba3c3c9ea5564d712731
# todo: можно реализовать через viewsets ModelViewSet
class UserList(ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = UserSerializer
