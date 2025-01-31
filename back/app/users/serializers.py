from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'image', 'wins', 'losses', 
                 'matches', 'logged', 'two_fa_enabled')
        read_only_fields = ('wins', 'losses', 'matches')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user 

class IntraUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    login = serializers.CharField()
    # Otros campos que quieras obtener de la API de 42
    
    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            email=validated_data['email'],
            defaults={
                'username': validated_data['login'],
                'password': 'intra42auth'  # Password temporal/aleatorio
            }
        )
        return user 