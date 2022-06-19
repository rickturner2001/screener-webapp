from rest_framework.serializers import ModelSerializer
from base.models import WatchList

class WatchlistSerializer(ModelSerializer):
    class Meta:
        model = WatchList
        fields = "__all__"