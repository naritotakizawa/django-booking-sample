from django.shortcuts import resolve_url
from django.test import TestCase


class StoreListViewTests(TestCase):
    fixtures = ['initial']

    def test_get(self):
        response = self.client.get(resolve_url('booking:store_list'))
        self.assertQuerysetEqual(response.context['store_list'],  ['<Store: 店舗A>', '<Store: 店舗B>', '<Store: 店舗C>'])


class StaffListViewTests(TestCase):
    fixtures = ['initial']

    def test_store_a(self):
        response = self.client.get(resolve_url('booking:staff_list', pk=1))
        self.assertQuerysetEqual(response.context['staff_list'],  ['<Staff: 店舗A - ぱいそん>'])

    def test_store_b(self):
        response = self.client.get(resolve_url('booking:staff_list', pk=2))
        self.assertQuerysetEqual(response.context['staff_list'],  ['<Staff: 店舗B - じゃんご>'])

    def test_store_c(self):
        response = self.client.get(resolve_url('booking:staff_list', pk=3))
        self.assertQuerysetEqual(response.context['staff_list'],  [])
