from django.shortcuts import reverse
from django.test import TestCase


class StoreListViewTests(TestCase):
    fixtures = ['initial']

    def test_get(self):
        response = self.client.get(reverse('booking:store_list'))
        self.assertQuerysetEqual(response.context['store_list'],  ['<Store: 店舗A>', '<Store: 店舗B>', '<Store: 店舗C>'])


class StaffListViewTests(TestCase):
    fixtures = ['initial']

    def test_store_a(self):
        pass

    def test_store_b(self):
        pass

    def test_store_c(self):
        pass
