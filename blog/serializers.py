from django.contrib.auth.models import User
from rest_framework import serializers
from wagtail.core.rich_text import RichText


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name' , 'email']


def get_place_serializer():
    from blog.models import Place


    class PlaceSerializer(serializers.ModelSerializer):
        class Meta:
            model = Place
            fields = ['name', 'address', 'lat', 'lng']
    return  PlaceSerializer()


class RichTextRendereableField(serializers.CharField):
    def to_representation(self, value):
        rich_text = RichText(value)
        return rich_text.__html__()















