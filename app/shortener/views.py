from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
import random
import string
from .models import ShortURL
from .serializers import ShortURLSerializer, CreateShortURLSerializer
from django.shortcuts import redirect
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class CreateShortURLView(APIView):
    """
        Create a short URL from a long URL
    """
    throttle_classes = [AnonRateThrottle]

    def generate_short_code(self):
        chars = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choices(chars, k=6))
            if not ShortURL.objects.filter(short_code=code).exists():
                return code

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['original_url'],
            properties={
                'original_url': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The original URL to be shortened',
                    example='https://www.youtube.com/'
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="Successfully created short URL",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'short_url': openapi.Schema(type=openapi.TYPE_STRING),
                        'expiration_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        'reason': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        nullable=True,
                        default=None,
                        example=None,
                        description='Always null when successful'
                    )
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid input",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        'reason': openapi.Schema(type=openapi.TYPE_STRING, example="Invalid URL format")
                    }
                )
            )
        }
    )
    def post(self, request):
        """
            Create a short URL
        """
        create_serializer = CreateShortURLSerializer(data=request.data)

        if not create_serializer.is_valid():
            return Response({
                'success': False,
                'reason': create_serializer.errors.get('original_url', ['Invalid URL format'])[0]
            }, status=status.HTTP_400_BAD_REQUEST)

        original_url = create_serializer.validated_data['original_url']

        short_url = ShortURL.objects.create(
            original_url=original_url,
            short_code=self.generate_short_code()
        )

        serializer = ShortURLSerializer(short_url, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RedirectShortURLView(APIView):
    def get(self, request, short_code):
        try:
            short_url = ShortURL.objects.get(short_code=short_code)

            if short_url.expiration_date < timezone.now():
                return Response({
                    'success': False,
                    'reason': 'URL has expired'
                }, status=status.HTTP_410_GONE)

            return redirect(short_url.original_url)

        except ShortURL.DoesNotExist:
            return Response({
                'success': False,
                'reason': 'Invalid short URL'
            }, status=status.HTTP_404_NOT_FOUND)
