from django.test import TestCase

# Create your tests here.
# from ..models import Player, Card, Deck, Action, Game, CardInstance, ActionHistory
from django.urls import reverse


class GameviewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        pass
        # Create 13 authors for pagination tests
        # number_of_authors = 13
        # for author_num in range(number_of_authors):
        # Author.objects.create(first_name='Christian %s' % author_num, last_name='Surname %s' % author_num, )

    # def test_view_url_exists_at_desired_location(self):
    #     resp = self.client.get('/coup/')
    #     self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('actions'))
        self.assertEqual(resp.status_code, 200)
