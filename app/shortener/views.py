from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
import random
import string
from .models import ShortURL
from .serializers import ShortURLSerializer, CreateShortURLSerializer


class CreateShortURLView(APIView):
    throttle_classes = [AnonRateThrottle]

    def generate_short_code(self):
        chars = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choices(chars, k=6))
            if not ShortURL.objects.filter(short_code=code).exists():
                return code

    def post(self, request):
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
