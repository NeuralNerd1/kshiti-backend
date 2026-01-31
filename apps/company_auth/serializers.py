from rest_framework import serializers
from .models import Company

class LoginSerializer(serializers.Serializer):
    company_slug = serializers.SlugField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        # Shape-level validation only (no auth here)
        if not attrs.get("company_slug"):
            raise serializers.ValidationError("company_slug is required")

        if not attrs.get("email"):
            raise serializers.ValidationError("email is required")

        if not attrs.get("password"):
            raise serializers.ValidationError("password is required")

        return attrs

class SessionSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField()
    user_id = serializers.IntegerField(required=False)
    email = serializers.EmailField(required=False)
    company_id = serializers.IntegerField(required=False)
    company_slug = serializers.SlugField(required=False)


class LogoutSerializer(serializers.Serializer):
    confirm = serializers.BooleanField(required=True)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)

class CompanyPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "slug"]
        read_only_fields = fields

