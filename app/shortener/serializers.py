from rest_framework import serializers
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
from .models import ShortURL


class CreateShortURLSerializer(serializers.Serializer):
    original_url = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages={
            'max_length': 'Ensure original_url field has no more than 2048 characters.',
            'required': 'The original_url field is required.'
        }
    )

    def validate_original_url(self, value):
        url_validator = URLValidator()
        try:
            url_validator(value)
            parsed_url = urlparse(value)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                raise ValidationError("Invalid URL format")
            if parsed_url.scheme not in ['http', 'https']:
                raise ValidationError("URL must use HTTP or HTTPS protocol")
            return value
        except ValidationError:
            raise serializers.ValidationError("Invalid URL format")


class ShortURLSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()
    success = serializers.SerializerMethodField()
    reason = serializers.SerializerMethodField()

    class Meta:
        model = ShortURL
        fields = ['short_url', 'expiration_date', 'success', 'reason']

    def get_short_url(self, obj):
        request = self.context.get('request')
        return f"{request.scheme}://{request.get_host()}/s/{obj.short_code}"

    def get_success(self, obj):
        return True

    def get_reason(self, obj):
        return None
