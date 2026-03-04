from rest_framework import serializers
from .models import ForensicAnalysis

class ForensicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForensicAnalysis
        fields = '__all__'