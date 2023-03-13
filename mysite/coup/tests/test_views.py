from django.test import TestCase

# Create your tests here.
from django.urls import reverse


class GameviewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/coup/")
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("authors"))
        self.assertEqual(resp.status_code, 200)
