from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import WatchlistSerializer
from base.api.market_data.api_requests import general_market_data_request


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
def get_routes(request):
    routes = [
        "api/token",
        "api/token/refresh",
    ]

    return Response(routes)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_watchlists(request):
    user = request.user
    watchlists = user.watchlist_set.all()
    serializer = WatchlistSerializer(watchlists, many=True)
    return Response(serializer.data)


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_general_market_data(request):
    return Response(general_market_data_request())
