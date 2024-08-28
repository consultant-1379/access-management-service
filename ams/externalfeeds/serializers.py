from rest_framework import serializers
from .models import *

class HydraInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HydraInfo
        fields = '__all__'

class DTTInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DTTInfo
        fields = '__all__'

class DITInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = DITInfo
        fields = '__all__'