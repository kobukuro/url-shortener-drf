from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from shortener.models import ShortURL
from django.utils import timezone
from datetime import timedelta


class CreateShortURLViewTests(APITestCase):
    def setUp(self):
        """Set up test data for URL shortening tests"""
        self.url = reverse('create_short_url')
        self.valid_payload = {
            'original_url': 'https://www.youtube.com/'
        }
        self.invalid_payload = {
            'original_url': 'not-a-valid-url'
        }

    def test_create_valid_short_url(self):
        """Test creating a valid short URL"""
        response = self.client.post(self.url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('short_url' in response.data)
        self.assertTrue('expiration_date' in response.data)
        self.assertTrue(ShortURL.objects.exists())

    def test_create_invalid_short_url(self):
        """Test creating an invalid short URL"""
        response = self.client.post(self.url, self.invalid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertTrue('reason' in response.data)

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Assuming rate limit is 10 requests per minute
        for _ in range(11):
            response = self.client.post(self.url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class RedirectShortURLViewTests(APITestCase):
    def setUp(self):
        """Set up test data for URL redirection tests"""
        # Create a valid short URL
        self.short_url = ShortURL.objects.create(
            original_url='https://www.youtube.com/',
            short_code='abc123',
            expiration_date=timezone.now() + timedelta(days=7)
        )

        # Create an expired short URL
        self.expired_url = ShortURL.objects.create(
            original_url='https://www.google.com/',
            short_code='def456',
            expiration_date=timezone.now() - timedelta(days=1)
        )

    def test_valid_redirect(self):
        """Test redirection for a valid short URL"""
        url = reverse('redirect_short_url', kwargs={'short_code': 'abc123'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, 'https://www.youtube.com/')

    def test_expired_url_redirect(self):
        """Test redirection for an expired short URL"""
        url = reverse('redirect_short_url', kwargs={'short_code': 'def456'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['reason'], 'URL has expired')

    def test_nonexistent_url_redirect(self):
        """Test redirection for a non-existent short URL"""
        url = reverse('redirect_short_url', kwargs={'short_code': 'nonexist'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['reason'], 'Invalid short URL')


class ShortURLModelTests(TestCase):
    def test_short_code_generation(self):
        """Test uniqueness of generated short codes"""
        url1 = ShortURL.objects.create(
            original_url='https://www.youtube.com/',
            short_code='abc123'
        )
        url2 = ShortURL.objects.create(
            original_url='https://www.google.com/',
            short_code='def456'
        )

        self.assertNotEqual(url1.short_code, url2.short_code)

    def test_expiration_date(self):
        """Test expiration date setting"""
        url = ShortURL.objects.create(
            original_url='https://www.youtube.com/',
            short_code='abc123'
        )

        self.assertTrue(url.expiration_date > timezone.now())
