from django.test import TestCase

# Create your tests here.
from django.urls import reverse


class LoginTests(TestCase):

    def page_redirect(self):
        url = reverse('gyara:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        url = reverse('gyara:in-view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        url = reverse('gyara:add-trans')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        url = reverse('gyara:cat-view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


