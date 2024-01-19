from rest_framework import status, exceptions, response, request
from rest_framework_simplejwt import exceptions as jwt_exceptions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from users.backends.utils import get_backend
from users.simplejwt.decorators import move_refresh_token_to_cookie
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# from api.swagger import Errors

TOKEN_EXPIRED_MESSAGE = 'Token is invalid or expired'
class Register(TokenObtainPairView):

    GOOGLE_HELP_URL = "https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow?hl=pt-br"

    @move_refresh_token_to_cookie
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        token = request.data.get('access_token')

        backend = get_backend(kwargs['oauth2'])
        if not backend:
            return response.Response(
                {
                    'errors': f'Invalid provider {kwargs["oauth2"]}'
                }, status=status.HTTP_400_BAD_REQUEST)

        user_data = backend.get_user_data(token)
        if user_data:
            user = backend.do_auth(user_data)

            serializer = self.get_serializer()
            refresh = serializer.get_token(user)
            data = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'picture_url': user.picture_url,
                'email': user.email,
            }

            return response.Response(data, status.HTTP_200_OK)

        return response.Response(
            {
                'errors': 'Invalid token'
            }, status.HTTP_400_BAD_REQUEST)


class HandleRefreshMixin:

    def handle(self, request):
        try:
            request.data['refresh'] = request.COOKIES['refresh']
        except KeyError:
            raise exceptions.NotAuthenticated('Refresh cookie error.')

        return request


class HandlePostErrorMixin():

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except jwt_exceptions.TokenError:
            return response.Response({
                "errors": TOKEN_EXPIRED_MESSAGE
            }, status=status.HTTP_400_BAD_REQUEST)

        return response.Response(serializer.validated_data, status=status.HTTP_200_OK)


class RefreshJWTView(HandlePostErrorMixin, HandleRefreshMixin, TokenRefreshView):

    @move_refresh_token_to_cookie
    def post(self, request, *args, **kwargs):
        request = self.handle(request)
        return super().post(request, *args, **kwargs)


class BlacklistJWTView(HandlePostErrorMixin, HandleRefreshMixin, TokenBlacklistView):

    def post(self, request, *args, **kwargs):
        request = self.handle(request)
        return super().post(request, *args, **kwargs)
