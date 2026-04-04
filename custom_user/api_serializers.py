from rest_framework import serializers
from custom_user.models import User

class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'date_joined', 'is_superuser', 'is_staff', 'first_name', 'last_name', 'avatar_url')

    def get_avatar_url(self, obj):
        if hasattr(obj, 'pybb_profile') and obj.pybb_profile:
            try:
                return getattr(obj.pybb_profile, 'avatar_url', None)
            except Exception:
                return None
        return None

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=32)
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )