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
