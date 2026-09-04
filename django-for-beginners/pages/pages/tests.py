from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_status_code(self):
        # self.client is Django's built-in test client - it simulates
        # a GET request through the full URL -> view -> template flow
        # without needing a real running server. reverse('home') looks
        # up the URL by the name= given in pages/urls.py, so the test
        # doesn't break if the path string itself ever changes.
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class AboutPageTests(TestCase):
    def test_about_page_status_code(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
